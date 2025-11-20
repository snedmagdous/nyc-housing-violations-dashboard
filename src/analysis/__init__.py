"""
Analysis Module

Statistical and geospatial analysis of housing violations.
Includes temporal patterns, geospatial hotspots, and predictive risk models.
"""

# Import temporal analysis functions
from .temporal_analysis import (
    analyze_seasonal_patterns,
    analyze_day_of_week_patterns,
    get_violation_trends
)

# Import geospatial analysis functions
from .geospatial_analysis import (
    find_hotspots,
    calculate_concentration_by_neighborhood,
    find_building_clusters,
    get_borough_comparison
)

# Import predictive model functions
from .predictive_model import (
    calculate_risk_score_simple,
    predict_at_risk_buildings,
    predict_violation_likelihood_next_month
)

__all__ = [
    # Temporal
    "analyze_seasonal_patterns",
    "analyze_day_of_week_patterns",
    "get_violation_trends",
    # Geospatial
    "find_hotspots",
    "calculate_concentration_by_neighborhood",
    "find_building_clusters",
    "get_borough_comparison",
    # Predictive
    "calculate_risk_score_simple",
    "predict_at_risk_buildings",
    "predict_violation_likelihood_next_month",
]
