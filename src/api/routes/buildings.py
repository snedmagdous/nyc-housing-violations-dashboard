"""
Buildings API Routes

Endpoints for building-level data and statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.api.database import get_db
from src.api.schemas import (
    BuildingBase,
    BuildingDetail,
    BuildingListResponse
)

router = APIRouter(
    prefix="/api/buildings",
    tags=["buildings"]
)


@router.get("/", response_model=BuildingListResponse)
async def list_buildings(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    min_violations: Optional[int] = Query(None, description="Minimum total violations"),
    min_open_violations: Optional[int] = Query(None, description="Minimum open violations"),
    min_risk_score: Optional[float] = Query(None, description="Minimum risk score"),
    has_class_c: Optional[bool] = Query(None, description="Has Class C violations"),

    # Sorting
    sort_by: str = Query("risk_score", description="Sort by: risk_score, total_violations, open_violations"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),

    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),

    db: Session = Depends(get_db)
):
    """
    List buildings with aggregated violation statistics.

    **Useful for:**
    - Finding worst offender buildings
    - Filtering by violation counts
    - Sorting by risk scores

    **Example:**
    GET /api/buildings?borough=BRONX&min_violations=10&sort_by=risk_score&sort_order=desc

    **Returns:**
    Buildings ranked by specified criteria
    """

    query_parts = ["SELECT * FROM buildings WHERE 1=1"]
    params = {}

    # Add filters
    if borough:
        query_parts.append("AND boro = :borough")
        params["borough"] = borough.upper()

    if min_violations:
        query_parts.append("AND total_violations >= :min_violations")
        params["min_violations"] = min_violations

    if min_open_violations:
        query_parts.append("AND open_violations >= :min_open_violations")
        params["min_open_violations"] = min_open_violations

    if min_risk_score:
        query_parts.append("AND risk_score >= :min_risk_score")
        params["min_risk_score"] = min_risk_score

    if has_class_c:
        query_parts.append("AND class_c_count > 0")

    # Validate sort_by to prevent SQL injection
    valid_sort_columns = ["risk_score", "total_violations", "open_violations", "most_recent_violation_date"]
    if sort_by not in valid_sort_columns:
        sort_by = "risk_score"

    # Validate sort_order
    sort_order = sort_order.upper()
    if sort_order not in ["ASC", "DESC"]:
        sort_order = "DESC"

    # Add sorting
    query_parts.append(f"ORDER BY {sort_by} {sort_order}")

    # Pagination
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset
    query_parts.append("LIMIT :limit OFFSET :offset")

    # Execute query
    query_sql = " ".join(query_parts)
    result = db.execute(text(query_sql), params)
    buildings = result.mappings().all()

    # Get total count
    count_query = "SELECT COUNT(*) as total FROM buildings WHERE 1=1"
    count_params = {k: v for k, v in params.items() if k not in ['limit', 'offset']}

    if borough:
        count_query += " AND boro = :borough"
    if min_violations:
        count_query += " AND total_violations >= :min_violations"
    if min_open_violations:
        count_query += " AND open_violations >= :min_open_violations"
    if min_risk_score:
        count_query += " AND risk_score >= :min_risk_score"
    if has_class_c:
        count_query += " AND class_c_count > 0"

    count_result = db.execute(text(count_query), count_params)
    total = count_result.scalar()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "buildings": buildings
    }


@router.get("/{building_id}", response_model=BuildingDetail)
async def get_building(
    building_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific building.

    **Usage:**
    GET /api/buildings/85470

    **Returns:**
    Building details with all aggregated statistics
    """
    query = "SELECT * FROM buildings WHERE buildingid = :id"
    result = db.execute(text(query), {"id": building_id})
    building = result.mappings().first()

    if not building:
        raise HTTPException(
            status_code=404,
            detail=f"Building {building_id} not found"
        )

    return building


@router.get("/{building_id}/violations")
async def get_building_violations(
    building_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all violations for a specific building.

    **Usage:**
    GET /api/buildings/85470/violations

    **Returns:**
    List of all violations for this building, with pagination
    """
    # First check if building exists
    building_check = db.execute(
        text("SELECT buildingid FROM buildings WHERE buildingid = :id"),
        {"id": building_id}
    ).first()

    if not building_check:
        raise HTTPException(
            status_code=404,
            detail=f"Building {building_id} not found"
        )

    # Get violations for this building
    offset = (page - 1) * page_size

    query = """
    SELECT * FROM violations
    WHERE buildingid = :building_id
    ORDER BY inspectiondate DESC
    LIMIT :limit OFFSET :offset
    """

    result = db.execute(
        text(query),
        {"building_id": building_id, "limit": page_size, "offset": offset}
    )
    violations = result.mappings().all()

    # Get total count
    count_result = db.execute(
        text("SELECT COUNT(*) FROM violations WHERE buildingid = :building_id"),
        {"building_id": building_id}
    )
    total = count_result.scalar()

    return {
        "building_id": building_id,
        "total_violations": total,
        "page": page,
        "page_size": page_size,
        "violations": violations
    }


@router.get("/search")
async def search_buildings(
    q: str = Query(..., min_length=3, description="Search query (address, zip, etc.)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for buildings by address.

    **Usage:**
    GET /api/buildings/search?q=123+main+st

    **Returns:**
    Buildings matching the search query
    """
    # Clean up search query
    search_term = f"%{q}%"

    query = """
    SELECT * FROM buildings
    WHERE
        LOWER(full_address) LIKE LOWER(:search)
        OR CAST(zip AS TEXT) LIKE :search
        OR CAST(buildingid AS TEXT) = :exact_id
    ORDER BY total_violations DESC
    LIMIT :limit
    """

    result = db.execute(
        text(query),
        {"search": search_term, "exact_id": q, "limit": limit}
    )
    buildings = result.mappings().all()

    return {
        "query": q,
        "count": len(buildings),
        "buildings": buildings
    }


@router.get("/stats/top-offenders")
async def get_top_offenders(
    limit: int = Query(10, ge=1, le=100, description="Number of buildings to return"),
    borough: Optional[str] = Query(None, description="Filter by borough"),
    db: Session = Depends(get_db)
):
    """
    Get the worst offender buildings (highest risk scores).

    **Usage:**
    GET /api/buildings/stats/top-offenders?limit=10&borough=BRONX

    **Returns:**
    Top N buildings with highest risk scores
    """
    query = """
    SELECT
        buildingid,
        full_address,
        boro,
        total_violations,
        open_violations,
        class_c_count,
        severe_violations,
        risk_score
    FROM buildings
    WHERE 1=1
    """

    params = {"limit": limit}

    if borough:
        query += " AND boro = :borough"
        params["borough"] = borough.upper()

    query += " ORDER BY risk_score DESC LIMIT :limit"

    result = db.execute(text(query), params)
    buildings = result.mappings().all()

    return {
        "count": len(buildings),
        "borough_filter": borough,
        "top_offenders": buildings
    }
