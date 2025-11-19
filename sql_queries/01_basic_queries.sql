/*
 * Basic SQL Queries - NYC Housing Violations
 *
 * Demonstrates: SELECT, WHERE, ORDER BY, LIMIT, Basic Aggregations
 */

-- ============================================================
-- 1. Overview: Total violations by borough
-- ============================================================
SELECT
    boro,
    COUNT(*) as total_violations,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
FROM violations
WHERE boro IS NOT NULL
GROUP BY boro
ORDER BY total_violations DESC;


-- ============================================================
-- 2. Most recent open violations
-- ============================================================
SELECT
    violationid,
    full_address,
    violation_class,
    class_description,
    novdescription,
    inspectiondate,
    currentstatus
FROM violations
WHERE is_open = true
ORDER BY inspectiondate DESC
LIMIT 100;


-- ============================================================
-- 3. Violation severity distribution
-- ============================================================
SELECT
    violation_class,
    class_description,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM violations
GROUP BY violation_class, class_description
ORDER BY violation_class;


-- ============================================================
-- 4. Top 10 most common violation types
-- ============================================================
SELECT
    novdescription,
    COUNT(*) as occurrence_count,
    ROUND(AVG(CASE WHEN is_open THEN 1 ELSE 0 END) * 100, 1) as pct_still_open
FROM violations
WHERE novdescription IS NOT NULL
GROUP BY novdescription
ORDER BY occurrence_count DESC
LIMIT 10;


-- ============================================================
-- 5. Violations by year and quarter
-- ============================================================
SELECT
    inspection_year,
    inspection_quarter,
    COUNT(*) as total_violations,
    SUM(CASE WHEN is_severe THEN 1 ELSE 0 END) as severe_violations,
    SUM(CASE WHEN is_open THEN 1 ELSE 0 END) as open_violations
FROM violations
WHERE inspection_year IS NOT NULL
GROUP BY inspection_year, inspection_quarter
ORDER BY inspection_year DESC, inspection_quarter DESC;


-- ============================================================
-- 6. Buildings with most violations
-- ============================================================
SELECT
    b.buildingid,
    b.full_address,
    b.boro,
    b.total_violations,
    b.open_violations,
    b.severe_violations,
    b.risk_score
FROM buildings b
ORDER BY b.total_violations DESC
LIMIT 20;


-- ============================================================
-- 7. Average violations per building by borough
-- ============================================================
SELECT
    b.boro,
    COUNT(DISTINCT b.buildingid) as num_buildings,
    SUM(b.total_violations) as total_violations,
    ROUND(AVG(b.total_violations), 2) as avg_violations_per_building,
    ROUND(AVG(b.severe_violations), 2) as avg_severe_per_building
FROM buildings b
WHERE b.boro IS NOT NULL
GROUP BY b.boro
ORDER BY avg_violations_per_building DESC;


-- ============================================================
-- 8. Neighborhoods (NTA) with highest violation rates
-- ============================================================
SELECT
    nta,
    boro,
    COUNT(DISTINCT buildingid) as num_buildings,
    COUNT(*) as total_violations,
    ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT buildingid), 0), 2) as violations_per_building
FROM violations
WHERE nta IS NOT NULL
GROUP BY nta, boro
HAVING COUNT(DISTINCT buildingid) >= 10  -- Only neighborhoods with 10+ buildings
ORDER BY violations_per_building DESC
LIMIT 15;


-- ============================================================
-- 9. Resolution rate by violation class
-- ============================================================
SELECT
    violation_class,
    COUNT(*) as total,
    SUM(CASE WHEN NOT is_open THEN 1 ELSE 0 END) as resolved,
    SUM(CASE WHEN is_open THEN 1 ELSE 0 END) as still_open,
    ROUND(SUM(CASE WHEN NOT is_open THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as resolution_rate_pct
FROM violations
GROUP BY violation_class
ORDER BY violation_class;


-- ============================================================
-- 10. Monthly violation trends
-- ============================================================
SELECT
    inspection_year,
    inspection_month,
    inspection_month_name,
    COUNT(*) as violations,
    AVG(severity_score) as avg_severity
FROM violations
WHERE inspection_year IS NOT NULL
  AND inspection_month IS NOT NULL
GROUP BY inspection_year, inspection_month, inspection_month_name
ORDER BY inspection_year DESC, inspection_month DESC
LIMIT 12;
