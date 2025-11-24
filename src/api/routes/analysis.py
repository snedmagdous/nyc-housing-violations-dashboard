"""
Analysis API Routes

Endpoints for ML models and advanced analysis:
- Temporal patterns
- Geospatial hotspots
- Predictive risk models
"""

from fastapi import APIRouter, Query
from typing import Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Import our analysis modules
from src.analysis import temporal_analysis, geospatial_analysis, predictive_model

router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"]
)


# =================== TEMPORAL ANALYSIS ===================

@router.get("/temporal/seasonal")
async def get_seasonal_patterns(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    violation_class: Optional[str] = Query(None, alias="class", description="Filter by class")
):
    """
    Get seasonal violation patterns.

    Shows which months have highest violation rates.
    Useful for predicting seasonal spikes (e.g., heating violations in winter).

    **Example:** `/api/analysis/temporal/seasonal?borough=BRONX`
    """
    result = temporal_analysis.analyze_seasonal_patterns(
        borough=borough,
        violation_class=violation_class
    )
    return result


@router.get("/temporal/day-of-week")
async def get_day_of_week_patterns():
    """
    Get day-of-week inspection patterns.

    Shows which days inspectors are most active.
    """
    result = temporal_analysis.analyze_day_of_week_patterns()
    return result


@router.get("/temporal/trends")
async def get_trends(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    months: int = Query(12, ge=1, le=36, description="Number of months to analyze")
):
    """
    Get violation trends over time.

    Shows if violations are increasing, decreasing, or stable.

    **Parameters:**
    - months: Number of recent months to analyze (default: 12)
    """
    result = temporal_analysis.get_violation_trends(
        borough=borough,
        months=months
    )
    return result


# =================== GEOSPATIAL ANALYSIS ===================

@router.get("/geospatial/hotspots")
async def get_hotspots(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    violation_class: Optional[str] = Query(None, alias="class"),
    grid_size_meters: int = Query(500, ge=100, le=2000, description="Grid cell size in meters"),
    min_violations: int = Query(5, ge=1, le=50, description="Minimum violations to be a hotspot")
):
    """
    Find geographic hotspots of violations.

    Uses spatial grid analysis to identify areas with high concentration of violations.
    Returns GeoJSON format for mapping.

    **Example:** `/api/analysis/geospatial/hotspots?borough=BRONX&grid_size_meters=1000`

    **Returns:**
    - hotspots: List of hotspot locations
    - geojson: GeoJSON FeatureCollection for mapping
    """
    result = geospatial_analysis.find_hotspots(
        borough=borough,
        violation_class=violation_class,
        grid_size_meters=grid_size_meters,
        min_violations=min_violations
    )
    return result


@router.get("/geospatial/neighborhoods")
async def get_neighborhood_concentration():
    """
    Get violation concentration by neighborhood (NTA).

    Shows which NYC neighborhoods have the most violations.

    **Returns:**
    - neighborhoods: All 300+ NYC neighborhoods with violation counts
    - top_10: Most affected neighborhoods
    """
    result = geospatial_analysis.calculate_concentration_by_neighborhood()
    return result


@router.get("/geospatial/building-clusters")
async def get_building_clusters(
    radius_meters: int = Query(250, ge=50, le=1000, description="Search radius in meters"),
    min_buildings: int = Query(3, ge=2, le=10, description="Minimum buildings to form cluster")
):
    """
    Find clusters of problem buildings near each other.

    Identifies geographic areas where multiple high-violation buildings are concentrated.

    **Use case:** Target enforcement efforts in areas with multiple problem landlords.
    """
    result = geospatial_analysis.find_building_clusters(
        radius_meters=radius_meters,
        min_buildings=min_buildings
    )
    return result


@router.get("/geospatial/borough-comparison")
async def compare_boroughs():
    """
    Compare violation statistics across NYC boroughs.

    **Returns:**
    - Per-borough statistics
    - Violations per building (normalized)
    - Class distribution
    """
    result = geospatial_analysis.get_borough_comparison()
    return result


# =================== PREDICTIVE MODELS ===================

@router.get("/predictions/building-risk/{building_id}")
async def get_building_risk(building_id: int):
    """
    Calculate risk score for a specific building.

    Predicts likelihood of future violations based on:
    - Historical violation patterns
    - Recent activity
    - Open violations
    - Severity of past violations

    **Returns:**
    - risk_score: 0-100 (higher = more risk)
    - risk_level: low, medium, high, or critical
    - contributing_factors: What's driving the risk
    - recommendations: Suggested actions

    **Example:** `/api/analysis/predictions/building-risk/62306`
    """
    result = predictive_model.calculate_risk_score_simple(building_id)
    return result


@router.get("/predictions/at-risk-buildings")
async def get_at_risk_buildings(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    limit: int = Query(50, ge=1, le=200, description="Number of buildings to return")
):
    """
    Get buildings most at risk of future violations.

    Ranks all buildings by risk score to identify those needing proactive intervention.

    **Use case:** Prioritize inspection resources on highest-risk buildings.

    **Returns:**
    - at_risk_buildings: List ranked by risk score
    - statistics: Overall risk distribution
    """
    result = predictive_model.predict_at_risk_buildings(
        borough=borough,
        limit=limit
    )
    return result


@router.get("/predictions/next-month-forecast")
async def forecast_next_month(
    borough: Optional[str] = Query(None, description="Filter by borough")
):
    """
    Predict expected violations for next month.

    Uses historical seasonal patterns to forecast violation volume.

    **Use case:** Resource planning for inspection staff.

    **Returns:**
    - prediction: Expected violation count
    - confidence_interval: Range of likely values
    - interpretation: Human-readable forecast
    """
    result = predictive_model.predict_violation_likelihood_next_month(
        borough=borough
    )
    return result


# =================== COMBINED INSIGHTS ===================

@router.get("/stats")
async def get_stats():
    """
    Get basic statistics for the dashboard home page.

    Returns overall counts used by the frontend dashboard.
    """
    from src.api.database import engine
    from sqlalchemy import text

    with engine.connect() as conn:
        # Get total violations
        total_violations = conn.execute(text("SELECT COUNT(*) FROM violations")).scalar()

        # Get open violations
        open_violations = conn.execute(text("SELECT COUNT(*) FROM violations WHERE is_open = true")).scalar()

        # Get total buildings
        total_buildings = conn.execute(text("SELECT COUNT(*) FROM buildings")).scalar()

        # Get severe violations (Class B or C)
        severe_violations = conn.execute(text("SELECT COUNT(*) FROM violations WHERE is_severe = true")).scalar()

    return {
        "total_violations": total_violations or 0,
        "open_violations": open_violations or 0,
        "total_buildings": total_buildings or 0,
        "total_severe_violations": severe_violations or 0
    }


@router.get("/insights/worst-offenders")
async def get_worst_offenders(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get comprehensive report on worst offender buildings.

    Combines multiple analyses:
    - High risk scores
    - Recent violations
    - Geographic clustering

    **Perfect for:** Creating a "landlord watchlist"
    """
    # Get at-risk buildings
    at_risk = predictive_model.predict_at_risk_buildings(limit=limit)

    # Get building clusters (to see if they're near each other)
    clusters = geospatial_analysis.find_building_clusters()

    return {
        "worst_offenders": at_risk['at_risk_buildings'],
        "total_analyzed": at_risk['count'],
        "clusters_found": clusters['count'],
        "summary": f"Found {at_risk['count']} high-risk buildings with average risk score {at_risk['statistics']['avg_risk_score']:.1f}/100"
    }


@router.get("/insights/dashboard-summary")
async def get_dashboard_summary():
    """
    Get summary statistics for main dashboard.

    Returns key metrics across all analysis types.
    """
    # Get borough comparison
    boroughs = geospatial_analysis.get_borough_comparison()

    # Get top hotspots
    hotspots = geospatial_analysis.find_hotspots(min_violations=10, grid_size_meters=1000)

    # Get top at-risk buildings
    at_risk = predictive_model.predict_at_risk_buildings(limit=10)

    # Get seasonal pattern
    seasonal = temporal_analysis.analyze_seasonal_patterns()

    return {
        "boroughs": boroughs['boroughs'],
        "top_hotspot": hotspots['hotspots'][0] if hotspots['count'] > 0 else None,
        "highest_risk_building": at_risk['at_risk_buildings'][0] if at_risk['count'] > 0 else None,
        "seasonal_peak_month": seasonal.get('peak_month', {}).get('name'),
        "total_neighborhoods": 0  # Will add neighborhood count
    }
