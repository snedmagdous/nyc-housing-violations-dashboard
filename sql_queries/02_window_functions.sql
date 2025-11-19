/*
 * Window Functions - NYC Housing Violations
 *
 * Demonstrates: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD,
 *               PARTITION BY, Moving Averages, Cumulative Stats
 */

-- ============================================================
-- 1. Rank buildings by total violations within each borough
-- ============================================================
SELECT
    buildingid,
    full_address,
    boro,
    total_violations,
    ROW_NUMBER() OVER (PARTITION BY boro ORDER BY total_violations DESC) as rank_in_borough,
    RANK() OVER (PARTITION BY boro ORDER BY total_violations DESC) as rank_with_ties,
    DENSE_RANK() OVER (PARTITION BY boro ORDER BY total_violations DESC) as dense_rank
FROM buildings
WHERE total_violations > 0
ORDER BY boro, total_violations DESC;


-- ============================================================
-- 2. Top 3 worst buildings per borough
-- ============================================================
WITH ranked_buildings AS (
    SELECT
        buildingid,
        full_address,
        boro,
        total_violations,
        open_violations,
        severe_violations,
        ROW_NUMBER() OVER (PARTITION BY boro ORDER BY risk_score DESC) as rn
    FROM buildings
    WHERE boro IS NOT NULL
)
SELECT
    boro,
    buildingid,
    full_address,
    total_violations,
    open_violations,
    severe_violations
FROM ranked_buildings
WHERE rn <= 3
ORDER BY boro, rn;


-- ============================================================
-- 3. Running total of violations over time
-- ============================================================
SELECT
    inspectiondate,
    COUNT(*) as daily_violations,
    SUM(COUNT(*)) OVER (ORDER BY inspectiondate) as cumulative_violations
FROM violations
WHERE inspectiondate IS NOT NULL
GROUP BY inspectiondate
ORDER BY inspectiondate DESC
LIMIT 100;


-- ============================================================
-- 4. Month-over-month violation growth
-- ============================================================
WITH monthly_counts AS (
    SELECT
        DATE_TRUNC('month', inspectiondate) as month,
        COUNT(*) as violations
    FROM violations
    WHERE inspectiondate IS NOT NULL
    GROUP BY DATE_TRUNC('month', inspectiondate)
)
SELECT
    month,
    violations,
    LAG(violations, 1) OVER (ORDER BY month) as prev_month,
    violations - LAG(violations, 1) OVER (ORDER BY month) as change,
    ROUND(
        (violations - LAG(violations, 1) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(violations, 1) OVER (ORDER BY month), 0),
        2
    ) as pct_change
FROM monthly_counts
ORDER BY month DESC;


-- ============================================================
-- 5. Moving average of violations (7-day window)
-- ============================================================
WITH daily_violations AS (
    SELECT
        inspectiondate,
        COUNT(*) as violations
    FROM violations
    WHERE inspectiondate IS NOT NULL
    GROUP BY inspectiondate
)
SELECT
    inspectiondate,
    violations,
    ROUND(AVG(violations) OVER (
        ORDER BY inspectiondate
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) as seven_day_avg,
    ROUND(AVG(violations) OVER (
        ORDER BY inspectiondate
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) as thirty_day_avg
FROM daily_violations
ORDER BY inspectiondate DESC
LIMIT 100;


-- ============================================================
-- 6. Percentile ranking of buildings by risk score
-- ============================================================
SELECT
    buildingid,
    full_address,
    boro,
    total_violations,
    risk_score,
    PERCENT_RANK() OVER (ORDER BY risk_score) as percentile,
    NTILE(10) OVER (ORDER BY risk_score) as decile,
    CASE
        WHEN PERCENT_RANK() OVER (ORDER BY risk_score) >= 0.9 THEN 'Top 10% (High Risk)'
        WHEN PERCENT_RANK() OVER (ORDER BY risk_score) >= 0.75 THEN 'Top 25% (Elevated Risk)'
        WHEN PERCENT_RANK() OVER (ORDER BY risk_score) >= 0.5 THEN 'Top 50% (Moderate Risk)'
        ELSE 'Lower 50% (Low Risk)'
    END as risk_category
FROM buildings
WHERE risk_score IS NOT NULL
ORDER BY risk_score DESC
LIMIT 100;


-- ============================================================
-- 7. Time between violations for each building
-- ============================================================
WITH building_violations AS (
    SELECT
        buildingid,
        full_address,
        inspectiondate,
        LAG(inspectiondate) OVER (PARTITION BY buildingid ORDER BY inspectiondate) as prev_inspection
    FROM violations
    WHERE inspectiondate IS NOT NULL
)
SELECT
    buildingid,
    full_address,
    inspectiondate,
    prev_inspection,
    inspectiondate - prev_inspection as days_since_last_violation
FROM building_violations
WHERE prev_inspection IS NOT NULL
ORDER BY days_since_last_violation
LIMIT 100;


-- ============================================================
-- 8. Violation class distribution per building (pivot style)
-- ============================================================
SELECT
    buildingid,
    full_address,
    boro,
    total_violations,
    class_a_count,
    class_b_count,
    class_c_count,
    class_i_count,
    ROUND(class_a_count * 100.0 / NULLIF(total_violations, 0), 1) as pct_class_a,
    ROUND(class_b_count * 100.0 / NULLIF(total_violations, 0), 1) as pct_class_b,
    ROUND(class_c_count * 100.0 / NULLIF(total_violations, 0), 1) as pct_class_c
FROM buildings
WHERE total_violations >= 5
ORDER BY (class_b_count + class_c_count) DESC
LIMIT 50;


-- ============================================================
-- 9. First and last violation dates for each building
-- ============================================================
SELECT
    buildingid,
    full_address,
    boro,
    FIRST_VALUE(inspectiondate) OVER (
        PARTITION BY buildingid
        ORDER BY inspectiondate
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as first_violation,
    LAST_VALUE(inspectiondate) OVER (
        PARTITION BY buildingid
        ORDER BY inspectiondate
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_violation,
    LAST_VALUE(inspectiondate) OVER (
        PARTITION BY buildingid
        ORDER BY inspectiondate
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) - FIRST_VALUE(inspectiondate) OVER (
        PARTITION BY buildingid
        ORDER BY inspectiondate
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as days_span
FROM violations
WHERE buildingid IS NOT NULL
  AND inspectiondate IS NOT NULL
ORDER BY buildingid, inspectiondate
LIMIT 100;


-- ============================================================
-- 10. Quarterly comparison with same quarter last year
-- ============================================================
WITH quarterly_stats AS (
    SELECT
        inspection_year,
        inspection_quarter,
        COUNT(*) as violations,
        AVG(severity_score) as avg_severity
    FROM violations
    WHERE inspection_year IS NOT NULL
    GROUP BY inspection_year, inspection_quarter
)
SELECT
    inspection_year,
    inspection_quarter,
    violations,
    avg_severity,
    LAG(violations, 4) OVER (ORDER BY inspection_year, inspection_quarter) as same_quarter_last_year,
    violations - LAG(violations, 4) OVER (ORDER BY inspection_year, inspection_quarter) as yoy_change,
    ROUND(
        (violations - LAG(violations, 4) OVER (ORDER BY inspection_year, inspection_quarter)) * 100.0 /
        NULLIF(LAG(violations, 4) OVER (ORDER BY inspection_year, inspection_quarter), 0),
        2
    ) as yoy_pct_change
FROM quarterly_stats
ORDER BY inspection_year DESC, inspection_quarter DESC;
