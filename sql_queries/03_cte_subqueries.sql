/*
 * CTEs and Subqueries - NYC Housing Violations
 *
 * Demonstrates: WITH clause (CTEs), nested subqueries,
 *               complex multi-step analysis
 */

-- ============================================================
-- 1. Multi-level CTE: Building risk assessment pipeline
-- ============================================================
WITH building_metrics AS (
    -- Step 1: Calculate raw metrics
    SELECT
        buildingid,
        full_address,
        boro,
        total_violations,
        open_violations,
        severe_violations,
        most_recent_violation_date
    FROM buildings
    WHERE total_violations > 0
),
risk_scores AS (
    -- Step 2: Calculate normalized risk components
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY total_violations) as violation_percentile,
        PERCENT_RANK() OVER (ORDER BY severe_violations) as severity_percentile,
        PERCENT_RANK() OVER (ORDER BY open_violations) as open_percentile
    FROM building_metrics
),
final_risk AS (
    -- Step 3: Composite risk score
    SELECT
        *,
        (violation_percentile * 0.4 +
         severity_percentile * 0.4 +
         open_percentile * 0.2) * 100 as composite_risk_score
    FROM risk_scores
)
SELECT
    buildingid,
    full_address,
    boro,
    total_violations,
    open_violations,
    severe_violations,
    ROUND(composite_risk_score, 2) as risk_score,
    CASE
        WHEN composite_risk_score >= 90 THEN 'CRITICAL'
        WHEN composite_risk_score >= 75 THEN 'HIGH'
        WHEN composite_risk_score >= 50 THEN 'MODERATE'
        ELSE 'LOW'
    END as risk_level
FROM final_risk
ORDER BY composite_risk_score DESC
LIMIT 50;


-- ============================================================
-- 2. Recursive CTE: Violation escalation chain
--    (Find buildings where violations got progressively worse)
-- ============================================================
WITH RECURSIVE violation_chain AS (
    -- Base case: First violation for each building
    SELECT
        buildingid,
        violationid,
        inspectiondate,
        severity_score,
        1 as sequence_num,
        ARRAY[severity_score] as severity_path
    FROM (
        SELECT
            buildingid,
            violationid,
            inspectiondate,
            severity_score,
            ROW_NUMBER() OVER (PARTITION BY buildingid ORDER BY inspectiondate) as rn
        FROM violations
        WHERE severity_score > 0
    ) first_violations
    WHERE rn = 1

    UNION ALL

    -- Recursive case: Next violation if severity increased
    SELECT
        v.buildingid,
        v.violationid,
        v.inspectiondate,
        v.severity_score,
        vc.sequence_num + 1,
        vc.severity_path || v.severity_score
    FROM violations v
    INNER JOIN violation_chain vc
        ON v.buildingid = vc.buildingid
        AND v.inspectiondate > vc.inspectiondate
        AND v.severity_score > vc.severity_score
    WHERE vc.sequence_num < 10  -- Limit recursion depth
)
SELECT
    vc.buildingid,
    b.full_address,
    b.boro,
    MAX(vc.sequence_num) as escalation_length,
    STRING_AGG(vc.severity_score::text, ' -> ' ORDER BY vc.sequence_num) as escalation_path
FROM violation_chain vc
JOIN buildings b ON vc.buildingid = b.buildingid
GROUP BY vc.buildingid, b.full_address, b.boro
HAVING MAX(vc.sequence_num) >= 3  -- At least 3 escalating violations
ORDER BY escalation_length DESC
LIMIT 25;


-- ============================================================
-- 3. Correlated subquery: Buildings worse than neighborhood average
-- ============================================================
SELECT
    b.buildingid,
    b.full_address,
    b.nta as neighborhood,
    b.total_violations,
    (
        SELECT AVG(b2.total_violations)
        FROM buildings b2
        WHERE b2.nta = b.nta
    ) as neighborhood_avg,
    b.total_violations - (
        SELECT AVG(b2.total_violations)
        FROM buildings b2
        WHERE b2.nta = b.nta
    ) as violations_above_avg,
    (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY b2.total_violations)
        FROM buildings b2
        WHERE b2.nta = b.nta
    ) as neighborhood_median
FROM buildings b
WHERE b.nta IS NOT NULL
    AND b.total_violations > (
        SELECT AVG(b2.total_violations)
        FROM buildings b2
        WHERE b2.nta = b.nta
    )
ORDER BY violations_above_avg DESC
LIMIT 50;


-- ============================================================
-- 4. CTE with JOIN: Landlord repeat offender analysis
--    (Find buildings with similar addresses - same landlord)
-- ============================================================
WITH address_components AS (
    SELECT
        buildingid,
        full_address,
        boro,
        total_violations,
        open_violations,
        SPLIT_PART(streetname, ' ', 1) as street_prefix,
        streetname
    FROM buildings b
    INNER JOIN (
        SELECT DISTINCT buildingid, streetname
        FROM violations
        WHERE streetname IS NOT NULL
    ) v ON b.buildingid = v.buildingid
    WHERE total_violations > 0
),
street_aggregates AS (
    SELECT
        streetname,
        boro,
        COUNT(DISTINCT buildingid) as buildings_on_street,
        SUM(total_violations) as total_street_violations,
        SUM(open_violations) as total_street_open_violations,
        AVG(total_violations) as avg_violations_per_building
    FROM address_components
    GROUP BY streetname, boro
    HAVING COUNT(DISTINCT buildingid) >= 3  -- At least 3 buildings
)
SELECT
    sa.streetname,
    sa.boro,
    sa.buildings_on_street,
    sa.total_street_violations,
    sa.total_street_open_violations,
    ROUND(sa.avg_violations_per_building, 2) as avg_per_building,
    ROUND(sa.total_street_violations::numeric / sa.buildings_on_street, 2) as violations_per_building
FROM street_aggregates sa
ORDER BY sa.total_street_violations DESC
LIMIT 30;


-- ============================================================
-- 5. Nested subqueries: Top violations in top neighborhoods
-- ============================================================
SELECT
    v.nta as neighborhood,
    v.novdescription as violation_type,
    COUNT(*) as occurrence_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY v.nta), 2) as pct_of_neighborhood
FROM violations v
WHERE v.nta IN (
    -- Subquery: Top 10 neighborhoods by total violations
    SELECT nta
    FROM (
        SELECT
            nta,
            COUNT(*) as total_violations
        FROM violations
        WHERE nta IS NOT NULL
        GROUP BY nta
        ORDER BY total_violations DESC
        LIMIT 10
    ) top_neighborhoods
)
GROUP BY v.nta, v.novdescription
HAVING COUNT(*) >= 5  -- At least 5 occurrences
ORDER BY v.nta, occurrence_count DESC;


-- ============================================================
-- 6. CTE with window functions: Violation velocity analysis
--    (How fast are violations accumulating?)
-- ============================================================
WITH monthly_building_violations AS (
    SELECT
        buildingid,
        DATE_TRUNC('month', inspectiondate) as month,
        COUNT(*) as monthly_violations
    FROM violations
    WHERE inspectiondate >= CURRENT_DATE - INTERVAL '12 months'
      AND buildingid IS NOT NULL
    GROUP BY buildingid, DATE_TRUNC('month', inspectiondate)
),
violation_velocity AS (
    SELECT
        buildingid,
        month,
        monthly_violations,
        AVG(monthly_violations) OVER (
            PARTITION BY buildingid
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as three_month_avg,
        monthly_violations - LAG(monthly_violations) OVER (
            PARTITION BY buildingid
            ORDER BY month
        ) as month_over_month_change
    FROM monthly_building_violations
)
SELECT
    vv.buildingid,
    b.full_address,
    b.boro,
    vv.month,
    vv.monthly_violations,
    ROUND(vv.three_month_avg, 2) as three_month_avg,
    vv.month_over_month_change,
    CASE
        WHEN vv.month_over_month_change > 0 THEN 'ACCELERATING'
        WHEN vv.month_over_month_change < 0 THEN 'DECELERATING'
        ELSE 'STABLE'
    END as trend
FROM violation_velocity vv
JOIN buildings b ON vv.buildingid = b.buildingid
WHERE vv.three_month_avg >= 2  -- At least 2 violations per month on average
ORDER BY vv.three_month_avg DESC, vv.buildingid, vv.month DESC
LIMIT 100;


-- ============================================================
-- 7. Complex CTE: Cohort analysis - when do violations get resolved?
-- ============================================================
WITH violation_cohorts AS (
    SELECT
        DATE_TRUNC('month', inspectiondate) as cohort_month,
        violationid,
        inspectiondate,
        currentstatusdate,
        is_open,
        EXTRACT(EPOCH FROM (currentstatusdate - inspectiondate)) / 86400 as days_to_resolution
    FROM violations
    WHERE inspectiondate >= CURRENT_DATE - INTERVAL '24 months'
),
cohort_metrics AS (
    SELECT
        cohort_month,
        COUNT(*) as total_violations,
        SUM(CASE WHEN NOT is_open THEN 1 ELSE 0 END) as resolved,
        AVG(CASE WHEN NOT is_open THEN days_to_resolution END) as avg_days_to_resolution,
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY CASE WHEN NOT is_open THEN days_to_resolution END
        ) as median_days_to_resolution
    FROM violation_cohorts
    GROUP BY cohort_month
)
SELECT
    cohort_month,
    total_violations,
    resolved,
    total_violations - resolved as still_open,
    ROUND(resolved * 100.0 / total_violations, 2) as resolution_rate_pct,
    ROUND(avg_days_to_resolution, 1) as avg_days_to_resolve,
    ROUND(median_days_to_resolution, 1) as median_days_to_resolve
FROM cohort_metrics
ORDER BY cohort_month DESC;


-- ============================================================
-- 8. Subquery in SELECT: Enriched building profile
-- ============================================================
SELECT
    b.buildingid,
    b.full_address,
    b.boro,
    b.total_violations,
    b.open_violations,
    (
        SELECT COUNT(DISTINCT violation_class)
        FROM violations v
        WHERE v.buildingid = b.buildingid
    ) as distinct_violation_types,
    (
        SELECT novdescription
        FROM violations v
        WHERE v.buildingid = b.buildingid
        GROUP BY novdescription
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) as most_common_violation,
    (
        SELECT MAX(inspectiondate)
        FROM violations v
        WHERE v.buildingid = b.buildingid
    ) as last_inspection,
    (
        SELECT COUNT(*)
        FROM violations v
        WHERE v.buildingid = b.buildingid
          AND v.inspectiondate >= CURRENT_DATE - INTERVAL '90 days'
    ) as violations_last_90_days
FROM buildings b
WHERE b.total_violations >= 5
ORDER BY b.total_violations DESC
LIMIT 50;
