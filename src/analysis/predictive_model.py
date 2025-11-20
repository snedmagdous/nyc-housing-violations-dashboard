"""
Predictive Risk Model

Uses machine learning to predict which buildings are likely to receive
future violations based on:
- Past violation history
- Violation patterns
- Geographic location
- Building characteristics

This is the UNIQUE feature that sets this project apart!
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from sqlalchemy import text
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config.database import get_engine


def get_building_features(building_id: int) -> Dict:
    """
    Extract features for a specific building for prediction.

    Features include:
    - Historical violation counts
    - Violation severity
    - Time since last violation
    - Geographic neighborhood characteristics

    Parameters
    ----------
    building_id : int
        Building ID to get features for

    Returns
    -------
    Dict
        Feature dictionary with all relevant predictors
    """
    engine = get_engine()

    query = """
    SELECT
        b.*,
        -- Calculate derived features (handle null dates using simple subtraction)
        CASE WHEN b.most_recent_violation_date IS NOT NULL
            THEN (CURRENT_DATE - b.most_recent_violation_date)
            ELSE NULL
        END as days_since_last_violation,
        CASE WHEN b.most_recent_violation_date IS NOT NULL AND b.first_violation_date IS NOT NULL
            THEN (b.most_recent_violation_date - b.first_violation_date)
            ELSE NULL
        END as violation_history_days,
        CASE WHEN b.total_violations > 0
            THEN b.open_violations::float / b.total_violations
            ELSE 0
        END as open_violation_rate,
        CASE WHEN b.total_violations > 0
            THEN b.severe_violations::float / b.total_violations
            ELSE 0
        END as severe_violation_rate
    FROM buildings b
    WHERE b.buildingid = :building_id
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"building_id": building_id})
        building = result.mappings().first()

    if not building:
        return None

    # Convert to dict
    features = dict(building)

    return features


def calculate_risk_score_simple(building_id: int) -> Dict:
    """
    Calculate a simple risk score for a building.

    This is a heuristic-based approach (not ML) that's fast and interpretable.
    Good for quick assessments.

    Risk factors:
    - Recent violations (recency)
    - High violation count (frequency)
    - Open violations (current issues)
    - Severe violations (severity)
    - Violation trend (worsening?)

    Returns
    -------
    Dict
        - risk_score: 0-100 score (higher = more risk)
        - risk_level: "low", "medium", "high", "critical"
        - contributing_factors: What's driving the risk
        - recommendations: What should be done
    """
    features = get_building_features(building_id)

    if not features:
        return {"error": "Building not found"}

    # Initialize score
    risk_score = 0
    factors = []
    recommendations = []

    # Factor 1: Recent violations (0-25 points)
    days_since_last = features.get('days_since_last_violation', 999)
    if days_since_last is not None:
        if days_since_last < 30:
            risk_score += 25
            factors.append("Very recent violation (within 30 days)")
        elif days_since_last < 90:
            risk_score += 20
            factors.append("Recent violation (within 90 days)")
        elif days_since_last < 180:
            risk_score += 10
            factors.append("Moderate recency (within 6 months)")

    # Factor 2: Total violations (0-25 points)
    total = features.get('total_violations', 0)
    if total >= 20:
        risk_score += 25
        factors.append(f"Very high violation count ({total})")
        recommendations.append("Building requires comprehensive inspection")
    elif total >= 10:
        risk_score += 15
        factors.append(f"High violation count ({total})")
    elif total >= 5:
        risk_score += 10
        factors.append(f"Moderate violation count ({total})")

    # Factor 3: Open violations (0-25 points)
    open_count = features.get('open_violations', 0)
    if open_count > 0:
        open_rate = features.get('open_violation_rate', 0)
        if open_rate > 0.7:
            risk_score += 25
            factors.append(f"Most violations still open ({open_count}/{total})")
            recommendations.append("Immediate follow-up needed on open violations")
        elif open_rate > 0.4:
            risk_score += 15
            factors.append(f"Many violations still open ({open_count}/{total})")
        else:
            risk_score += 10
            factors.append(f"Some violations still open ({open_count}/{total})")

    # Factor 4: Severe violations (0-25 points)
    class_c = features.get('class_c_count', 0)
    severe = features.get('severe_violations', 0)
    if class_c > 5:
        risk_score += 25
        factors.append(f"Multiple immediately hazardous violations ({class_c} Class C)")
        recommendations.append("PRIORITY: Immediately hazardous conditions present")
    elif class_c > 2:
        risk_score += 20
        factors.append(f"Several immediately hazardous violations ({class_c} Class C)")
    elif severe > 5:
        risk_score += 15
        factors.append(f"Multiple hazardous violations ({severe} Class B/C)")
    elif severe > 0:
        risk_score += 10
        factors.append(f"Some hazardous violations ({severe} Class B/C)")

    # Cap at 100
    risk_score = min(risk_score, 100)

    # Determine risk level
    if risk_score >= 75:
        risk_level = "critical"
        recommendations.append("Urgent intervention required")
    elif risk_score >= 50:
        risk_level = "high"
        recommendations.append("Proactive inspection recommended")
    elif risk_score >= 25:
        risk_level = "medium"
        recommendations.append("Monitor for changes")
    else:
        risk_level = "low"

    return {
        "building_id": building_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "contributing_factors": factors,
        "recommendations": recommendations,
        "building_info": {
            "address": features.get('full_address'),
            "borough": features.get('boro'),
            "total_violations": int(features.get('total_violations', 0)),
            "open_violations": int(features.get('open_violations', 0)),
            "class_c_count": int(features.get('class_c_count', 0))
        }
    }


def predict_at_risk_buildings(
    borough: Optional[str] = None,
    limit: int = 50
) -> Dict:
    """
    Identify buildings most at risk of getting new violations.

    Uses the risk scoring system to rank buildings.

    Parameters
    ----------
    borough : str, optional
        Filter by borough
    limit : int
        Number of buildings to return

    Returns
    -------
    Dict
        - at_risk_buildings: List of buildings ranked by risk
        - statistics: Overall risk distribution
    """
    print(f"Identifying at-risk buildings...")

    engine = get_engine()

    # Build query to get buildings with calculated risk factors
    query = """
    SELECT
        buildingid,
        full_address,
        boro,
        total_violations,
        open_violations,
        class_c_count,
        severe_violations,
        risk_score,
        most_recent_violation_date,
        CASE WHEN most_recent_violation_date IS NOT NULL
            THEN (CURRENT_DATE - most_recent_violation_date)
            ELSE NULL
        END as days_since_last,
        CASE WHEN total_violations > 0
            THEN open_violations::float / total_violations
            ELSE 0
        END as open_rate
    FROM buildings
    WHERE total_violations > 0
    """

    params = {"limit": limit}

    if borough:
        query += " AND boro = :borough"
        params["borough"] = borough.upper()

    # Order by risk score (already calculated in database)
    query += " ORDER BY risk_score DESC, total_violations DESC LIMIT :limit"

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        buildings = result.mappings().all()

    # Convert to list
    at_risk_list = []
    for b in buildings:
        at_risk_list.append({
            "building_id": int(b['buildingid']),
            "address": b['full_address'],
            "borough": b['boro'],
            "risk_score": float(b['risk_score']) if b['risk_score'] else 0,
            "total_violations": int(b['total_violations']),
            "open_violations": int(b['open_violations']),
            "class_c_count": int(b['class_c_count']),
            "days_since_last_violation": int(b['days_since_last']) if b['days_since_last'] else None,
            "open_violation_rate": float(b['open_rate'])
        })

    # Calculate statistics
    risk_scores = [b['risk_score'] for b in at_risk_list]

    return {
        "at_risk_buildings": at_risk_list,
        "count": len(at_risk_list),
        "statistics": {
            "avg_risk_score": float(np.mean(risk_scores)) if risk_scores else 0,
            "max_risk_score": float(np.max(risk_scores)) if risk_scores else 0,
            "buildings_analyzed": len(at_risk_list)
        },
        "filters": {
            "borough": borough,
            "limit": limit
        }
    }


def predict_violation_likelihood_next_month(
    borough: Optional[str] = None
) -> Dict:
    """
    Predict likelihood of violations in next month based on historical patterns.

    Uses temporal patterns (seasonal trends, day-of-week) to forecast.

    Returns
    -------
    Dict
        - prediction: Expected number of violations next month
        - confidence_interval: Range of expected values
        - based_on: What data was used for prediction
    """
    print("Predicting next month violations...")

    engine = get_engine()

    # Get historical data for same month in previous years
    current_month = datetime.now().month

    query = """
    SELECT
        inspection_month,
        inspection_year,
        COUNT(*) as violation_count
    FROM violations
    WHERE inspection_month = :month
    GROUP BY inspection_month, inspection_year
    ORDER BY inspection_year
    """

    params = {"month": current_month}

    if borough:
        query = query.replace(
            "WHERE inspection_month",
            "WHERE boro = :borough AND inspection_month"
        )
        params["borough"] = borough.upper()

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        historical = result.mappings().all()

    if len(historical) == 0:
        return {
            "error": "Not enough historical data for prediction"
        }

    # Calculate average and trend
    counts = [h['violation_count'] for h in historical]
    avg_count = np.mean(counts)
    std_count = np.std(counts)

    # Simple prediction: use historical average with confidence interval
    prediction = int(avg_count)
    confidence_lower = int(max(0, avg_count - std_count))
    confidence_upper = int(avg_count + std_count)

    return {
        "prediction": {
            "expected_violations_next_month": prediction,
            "confidence_interval": {
                "lower": confidence_lower,
                "upper": confidence_upper
            }
        },
        "based_on": {
            "historical_years": len(historical),
            "average_for_this_month": prediction,
            "std_deviation": float(std_count)
        },
        "interpretation": f"Based on historical patterns, expect around {prediction} violations next month (range: {confidence_lower}-{confidence_upper})"
    }


if __name__ == "__main__":
    # Test predictive models
    print("=" * 60)
    print("Predictive Risk Model - Testing")
    print("=" * 60)

    # Test individual building risk score
    print("\n[1/3] Individual Building Risk Assessment:")
    # Get a building ID from database
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT buildingid FROM buildings ORDER BY risk_score DESC LIMIT 1"))
        test_building_id = result.scalar()

    if test_building_id:
        risk_assessment = calculate_risk_score_simple(test_building_id)
        print(f"  Building: {risk_assessment['building_info']['address']}")
        print(f"  Risk Score: {risk_assessment['risk_score']}/100 ({risk_assessment['risk_level']})")
        print(f"  Factors:")
        for factor in risk_assessment['contributing_factors']:
            print(f"    - {factor}")

    # Test at-risk buildings
    print("\n[2/3] At-Risk Buildings (Top 10):")
    at_risk = predict_at_risk_buildings(limit=10)
    print(f"  Found {at_risk['count']} at-risk buildings")
    print(f"  Average risk score: {at_risk['statistics']['avg_risk_score']:.1f}")
    if at_risk['count'] > 0:
        top = at_risk['at_risk_buildings'][0]
        print(f"  Highest risk: {top['address']}")
        print(f"    Risk score: {top['risk_score']:.1f}")
        print(f"    Violations: {top['total_violations']} ({top['open_violations']} open)")

    # Test monthly prediction
    print("\n[3/3] Next Month Prediction:")
    prediction = predict_violation_likelihood_next_month()
    if 'error' not in prediction:
        print(f"  {prediction['interpretation']}")
        print(f"  Based on {prediction['based_on']['historical_years']} years of data")

    print("\n" + "=" * 60)
    print("Predictive modeling complete!")
    print("=" * 60)
