"""
Temporal Pattern Analysis

Analyzes violation trends over time to identify:
- Seasonal patterns (e.g., heating violations in winter)
- Long-term trends (increasing/decreasing over years)
- Day-of-week patterns
- Monthly distributions

This helps predict WHEN violations are likely to occur.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.database import get_engine


def get_violations_timeseries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    borough: Optional[str] = None,
    violation_class: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch violations data as time series.

    Parameters
    ----------
    start_date : str, optional
        Start date (YYYY-MM-DD)
    end_date : str, optional
        End date (YYYY-MM-DD)
    borough : str, optional
        Filter by borough
    violation_class : str, optional
        Filter by class (A, B, C, I)

    Returns
    -------
    pd.DataFrame
        DataFrame with violations indexed by date
    """
    engine = get_engine()

    query = """
    SELECT
        inspectiondate,
        class,
        boro,
        is_severe,
        inspection_year,
        inspection_month,
        inspection_month_name,
        inspection_day_of_week,
        inspection_quarter
    FROM violations
    WHERE inspectiondate IS NOT NULL
    """

    params = {}

    if start_date:
        query += " AND inspectiondate >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND inspectiondate <= :end_date"
        params["end_date"] = end_date

    if borough:
        query += " AND boro = :borough"
        params["borough"] = borough.upper()

    if violation_class:
        query += " AND class = :violation_class"
        params["violation_class"] = violation_class.upper()

    query += " ORDER BY inspectiondate"

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)

    df['inspectiondate'] = pd.to_datetime(df['inspectiondate'])
    return df


def analyze_seasonal_patterns(
    borough: Optional[str] = None,
    violation_class: Optional[str] = None
) -> Dict:
    """
    Analyze seasonal patterns in violations.

    Identifies which months/quarters have highest violation rates.

    Returns
    -------
    Dict
        - monthly_counts: Violations per month
        - quarterly_counts: Violations per quarter
        - seasonal_index: Ratio of each month to average (>1 = above average)
        - interpretation: Human-readable insights
    """
    print(f"Analyzing seasonal patterns...")

    df = get_violations_timeseries(borough=borough, violation_class=violation_class)

    if len(df) == 0:
        return {"error": "No data found for specified filters"}

    # Monthly aggregation
    monthly = df.groupby('inspection_month').size()
    monthly_names = df.groupby('inspection_month_name').size()

    # Quarterly aggregation
    quarterly = df.groupby('inspection_quarter').size()

    # Calculate seasonal index (ratio to average)
    avg_per_month = monthly.mean()
    seasonal_index = (monthly / avg_per_month).to_dict()

    # Find peaks and troughs
    peak_month = monthly.idxmax()
    trough_month = monthly.idxmin()

    # Get month names
    month_names = df[df['inspection_month'] == peak_month]['inspection_month_name'].iloc[0]
    trough_month_name = df[df['inspection_month'] == trough_month]['inspection_month_name'].iloc[0]

    # Interpretation
    interpretation = []

    if seasonal_index[peak_month] > 1.2:
        interpretation.append(
            f"Strong seasonal peak in {month_names} "
            f"({seasonal_index[peak_month]:.1%} above average)"
        )

    if seasonal_index[trough_month] < 0.8:
        interpretation.append(
            f"Significant drop in {trough_month_name} "
            f"({(1 - seasonal_index[trough_month]):.1%} below average)"
        )

    # Check for winter spike (heating violations)
    winter_months = [12, 1, 2]
    winter_avg = monthly[monthly.index.isin(winter_months)].mean()
    summer_months = [6, 7, 8]
    summer_avg = monthly[monthly.index.isin(summer_months)].mean()

    if winter_avg > summer_avg * 1.3:
        interpretation.append(
            f"Winter violations are {(winter_avg/summer_avg - 1):.1%} higher than summer "
            f"(likely heating/weatherization issues)"
        )

    return {
        "monthly_counts": monthly.to_dict(),
        "monthly_names": monthly_names.to_dict(),
        "quarterly_counts": quarterly.to_dict(),
        "seasonal_index": seasonal_index,
        "peak_month": {
            "month": int(peak_month),
            "name": month_names,
            "count": int(monthly[peak_month]),
            "index": float(seasonal_index[peak_month])
        },
        "trough_month": {
            "month": int(trough_month),
            "name": trough_month_name,
            "count": int(monthly[trough_month]),
            "index": float(seasonal_index[trough_month])
        },
        "interpretation": interpretation,
        "total_violations": len(df),
        "date_range": {
            "start": df['inspectiondate'].min().strftime('%Y-%m-%d'),
            "end": df['inspectiondate'].max().strftime('%Y-%m-%d')
        }
    }


def analyze_day_of_week_patterns() -> Dict:
    """
    Analyze which days of the week have most inspections/violations.

    Useful for understanding enforcement patterns.

    Returns
    -------
    Dict
        - day_counts: Violations per day of week
        - interpretation: Insights
    """
    print("Analyzing day-of-week patterns...")

    df = get_violations_timeseries()

    if len(df) == 0:
        return {"error": "No data found"}

    # Count by day of week
    day_counts = df.groupby('inspection_day_of_week').size()

    # Order days properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = day_counts.reindex(day_order, fill_value=0)

    # Find peak day
    peak_day = day_counts.idxmax()
    peak_count = day_counts[peak_day]

    # Weekday vs weekend
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    weekend = ['Saturday', 'Sunday']

    weekday_avg = day_counts[weekdays].mean()
    weekend_avg = day_counts[weekend].mean()

    interpretation = []
    interpretation.append(
        f"Most inspections occur on {peak_day} ({peak_count:,} violations)"
    )

    if weekend_avg > 0 and weekday_avg > weekend_avg * 2:
        interpretation.append(
            f"Weekday inspections are {(weekday_avg/weekend_avg):.1f}x more common than weekends"
        )
    elif weekend_avg == 0:
        interpretation.append(
            "No weekend inspections found (HPD typically doesn't inspect on weekends)"
        )

    return {
        "day_counts": day_counts.to_dict(),
        "peak_day": peak_day,
        "weekday_average": float(weekday_avg),
        "weekend_average": float(weekend_avg),
        "interpretation": interpretation
    }


def get_violation_trends(
    borough: Optional[str] = None,
    months: int = 12
) -> Dict:
    """
    Get violation trends over recent months.

    Shows if violations are increasing or decreasing.

    Parameters
    ----------
    borough : str, optional
        Filter by borough
    months : int
        Number of recent months to analyze

    Returns
    -------
    Dict
        - monthly_trend: Violations per month
        - trend_direction: "increasing", "decreasing", or "stable"
        - percent_change: Change from first to last month
    """
    print(f"Analyzing {months}-month trend...")

    # Get data from last N months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    df = get_violations_timeseries(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        borough=borough
    )

    if len(df) == 0:
        return {"error": "No data found"}

    # Group by year-month
    df['year_month'] = df['inspectiondate'].dt.to_period('M')
    monthly_trend = df.groupby('year_month').size()

    # Calculate trend
    if len(monthly_trend) < 2:
        return {"error": "Not enough data for trend analysis"}

    first_month = monthly_trend.iloc[0]
    last_month = monthly_trend.iloc[-1]
    percent_change = ((last_month - first_month) / first_month) * 100

    # Determine trend direction
    if percent_change > 10:
        trend_direction = "increasing"
    elif percent_change < -10:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"

    # Convert period to string for JSON
    monthly_trend_dict = {str(k): int(v) for k, v in monthly_trend.items()}

    return {
        "monthly_trend": monthly_trend_dict,
        "trend_direction": trend_direction,
        "percent_change": float(percent_change),
        "first_month": {
            "period": str(monthly_trend.index[0]),
            "count": int(first_month)
        },
        "last_month": {
            "period": str(monthly_trend.index[-1]),
            "count": int(last_month)
        },
        "months_analyzed": len(monthly_trend)
    }


if __name__ == "__main__":
    # Test the temporal analysis
    print("=" * 60)
    print("Temporal Pattern Analysis - Testing")
    print("=" * 60)

    # Test seasonal patterns
    print("\n[1/3] Seasonal Patterns:")
    seasonal = analyze_seasonal_patterns()
    print(f"  Peak month: {seasonal['peak_month']['name']} ({seasonal['peak_month']['count']:,} violations)")
    print(f"  Interpretations:")
    for interp in seasonal['interpretation']:
        print(f"    - {interp}")

    # Test day of week patterns
    print("\n[2/3] Day of Week Patterns:")
    dow = analyze_day_of_week_patterns()
    print(f"  Peak day: {dow['peak_day']}")
    for interp in dow['interpretation']:
        print(f"    - {interp}")

    # Test trends
    print("\n[3/3] Recent Trends (12 months):")
    trends = get_violation_trends(months=12)
    if 'error' in trends:
        print(f"  {trends['error']}")
    else:
        print(f"  Trend: {trends['trend_direction']}")
        print(f"  Change: {trends['percent_change']:.1f}%")

    print("\n" + "=" * 60)
    print("Temporal analysis complete!")
    print("=" * 60)
