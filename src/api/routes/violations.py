"""
Violations API Routes

This file contains all endpoints related to violations:
- List violations with filters
- Get single violation details
- Search violations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.api.database import get_db
from src.api.schemas import (
    ViolationBase,
    ViolationDetail,
    ViolationListResponse,
    ErrorResponse
)

# Create a router - this groups related endpoints together
router = APIRouter(
    prefix="/api/violations",
    tags=["violations"]  # Shows up in /docs as a category
)


@router.get("/", response_model=ViolationListResponse)
async def list_violations(
    # Query parameters (everything after ? in URL)
    borough: Optional[str] = Query(None, description="Filter by borough (BRONX, BROOKLYN, MANHATTAN, QUEENS, STATEN ISLAND)"),
    violation_class: Optional[str] = Query(None, alias="class", description="Filter by class (A, B, C, I)"),
    status: Optional[str] = Query(None, description="Filter by status (e.g., 'VIOLATION OPEN')"),
    zip_code: Optional[int] = Query(None, alias="zip", description="Filter by ZIP code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    is_severe: Optional[bool] = Query(None, description="Only severe violations (B or C)"),

    # Pagination
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(100, ge=1, le=1000, description="Results per page (max 1000)"),

    # Database session (automatically provided by FastAPI)
    db: Session = Depends(get_db)
):
    """
    Get a list of violations with optional filters.

    **How it works:**
    1. User requests: GET /api/violations?borough=BRONX&class=C&page=1&page_size=50
    2. This function receives the parameters
    3. Builds a SQL query with filters
    4. Returns JSON with violations + pagination info

    **Example Response:**
    ```json
    {
        "total": 445,
        "page": 1,
        "page_size": 50,
        "violations": [
            {
                "violationid": 18405284,
                "buildingid": 85470,
                "boro": "BRONX",
                "full_address": "1163 Hoe Avenue, BRONX, NY 10459",
                "class": "C",
                ...
            },
            ...
        ]
    }
    ```
    """

    # Build the base query
    # We select from violations table and use LIMIT/OFFSET for pagination
    query_parts = ["SELECT * FROM violations WHERE 1=1"]  # WHERE 1=1 makes it easy to add AND clauses
    params = {}

    # Add filters dynamically based on what user provided
    if borough:
        query_parts.append("AND boro = :borough")
        params["borough"] = borough.upper()

    if violation_class:
        query_parts.append("AND class = :violation_class")
        params["violation_class"] = violation_class.upper()

    if status:
        query_parts.append("AND currentstatus = :status")
        params["status"] = status.upper()

    if zip_code:
        query_parts.append("AND zip = :zip_code")
        params["zip_code"] = zip_code

    if is_open is not None:
        query_parts.append("AND is_open = :is_open")
        params["is_open"] = is_open

    if is_severe is not None:
        query_parts.append("AND is_severe = :is_severe")
        params["is_severe"] = is_severe

    # Calculate pagination
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    # Add ORDER BY and pagination
    query_parts.append("ORDER BY inspectiondate DESC")
    query_parts.append("LIMIT :limit OFFSET :offset")

    # Join all parts into final query
    query_sql = " ".join(query_parts)

    # Execute the query
    result = db.execute(text(query_sql), params)
    violations = result.mappings().all()  # Convert to list of dicts

    # Get total count (for pagination info)
    count_query = "SELECT COUNT(*) as total FROM violations WHERE 1=1"
    # Remove pagination-specific params for count
    count_params = {k: v for k, v in params.items() if k not in ['limit', 'offset']}

    # Add the same filters to count query
    if borough:
        count_query += " AND boro = :borough"
    if violation_class:
        count_query += " AND class = :violation_class"
    if status:
        count_query += " AND currentstatus = :status"
    if zip_code:
        count_query += " AND zip = :zip_code"
    if is_open is not None:
        count_query += " AND is_open = :is_open"
    if is_severe is not None:
        count_query += " AND is_severe = :is_severe"

    count_result = db.execute(text(count_query), count_params)
    total = count_result.scalar()

    # Return response matching our schema
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "violations": violations
    }


@router.get("/{violation_id}", response_model=ViolationDetail)
async def get_violation(
    violation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific violation.

    **Usage:**
    GET /api/violations/18405284

    **Returns:**
    Full violation details including all fields
    """
    query = "SELECT * FROM violations WHERE violationid = :id"
    result = db.execute(text(query), {"id": violation_id})
    violation = result.mappings().first()

    if not violation:
        raise HTTPException(
            status_code=404,
            detail=f"Violation {violation_id} not found"
        )

    return violation


@router.get("/search/address")
async def search_by_address(
    address: str = Query(..., description="Search term for address"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """
    Search violations by address.

    Uses PostgreSQL full-text search for better results.

    **Usage:**
    GET /api/violations/search/address?address=1163+Hoe+Avenue

    **Returns:**
    List of violations matching the address
    """
    # Use ILIKE for case-insensitive partial matching
    query = """
    SELECT * FROM violations
    WHERE full_address ILIKE :search_term
    ORDER BY inspectiondate DESC
    LIMIT :limit
    """

    search_term = f"%{address}%"  # Wrap with % for partial matching
    result = db.execute(text(query), {"search_term": search_term, "limit": limit})
    violations = result.mappings().all()

    return {
        "search_term": address,
        "results_count": len(violations),
        "violations": violations
    }
