/*
 * Geospatial Queries (PostGIS) - NYC Housing Violations
 *
 * Demonstrates: PostGIS functions, spatial joins, distance calculations,
 *               geographic clustering, proximity analysis
 */

-- ============================================================
-- 1. Find violations within 500 meters of a specific location
--    (Example: Near Times Square: 40.758, -73.9855)
-- ============================================================
SELECT
    violationid,
    full_address,
    boro,
    violation_class,
    novdescription,
    ST_Distance(
        geom::geography,
        ST_SetSRID(ST_MakePoint(-73.9855, 40.758), 4326)::geography
    ) as distance_meters
FROM violations
WHERE geom IS NOT NULL
  AND ST_DWithin(
      geom::geography,
      ST_SetSRID(ST_MakePoint(-73.9855, 40.758), 4326)::geography,
      500  -- 500 meters
  )
ORDER BY distance_meters
LIMIT 50;


-- ============================================================
-- 2. Find nearest buildings with violations to a point
-- ============================================================
WITH target_location AS (
    SELECT ST_SetSRID(ST_MakePoint(-73.935242, 40.730610), 4326)::geography as geom
    -- Example: Brooklyn location
)
SELECT
    b.buildingid,
    b.full_address,
    b.boro,
    b.total_violations,
    b.severe_violations,
    ROUND(
        ST_Distance(b.geom::geography, tl.geom)::numeric,
        2
    ) as distance_meters,
    ROUND(
        ST_Distance(b.geom::geography, tl.geom)::numeric * 0.000621371,
        2
    ) as distance_miles
FROM buildings b, target_location tl
WHERE b.geom IS NOT NULL
ORDER BY b.geom::geography <-> tl.geom
LIMIT 20;


-- ============================================================
-- 3. Cluster violations by geographic proximity (within 100m)
-- ============================================================
WITH clustered_violations AS (
    SELECT
        v1.violationid,
        v1.buildingid,
        v1.full_address,
        v1.boro,
        v1.geom,
        COUNT(DISTINCT v2.violationid) as nearby_violations
    FROM violations v1
    LEFT JOIN violations v2
        ON v1.violationid != v2.violationid
        AND v1.geom IS NOT NULL
        AND v2.geom IS NOT NULL
        AND ST_DWithin(
            v1.geom::geography,
            v2.geom::geography,
            100  -- 100 meters
        )
    WHERE v1.geom IS NOT NULL
    GROUP BY v1.violationid, v1.buildingid, v1.full_address, v1.boro, v1.geom
)
SELECT
    buildingid,
    full_address,
    boro,
    nearby_violations,
    ST_X(geom::geometry) as longitude,
    ST_Y(geom::geometry) as latitude
FROM clustered_violations
WHERE nearby_violations >= 10  -- Hotspot threshold
ORDER BY nearby_violations DESC
LIMIT 50;


-- ============================================================
-- 4. Calculate density: violations per square kilometer by neighborhood
-- ============================================================
WITH neighborhood_bounds AS (
    SELECT
        nta,
        boro,
        ST_ConvexHull(ST_Collect(geom::geometry)) as boundary,
        COUNT(*) as violation_count
    FROM violations
    WHERE geom IS NOT NULL
      AND nta IS NOT NULL
    GROUP BY nta, boro
)
SELECT
    nta,
    boro,
    violation_count,
    ROUND(
        ST_Area(boundary::geography) / 1000000.0,  -- Convert to km²
        2
    ) as area_km2,
    ROUND(
        violation_count::numeric / NULLIF(ST_Area(boundary::geography) / 1000000.0, 0),
        2
    ) as violations_per_km2,
    ST_AsText(ST_Centroid(boundary)) as centroid
FROM neighborhood_bounds
WHERE ST_Area(boundary::geography) > 0
ORDER BY violations_per_km2 DESC
LIMIT 20;


-- ============================================================
-- 5. Find buildings within a polygon (bounding box)
--    (Example: Manhattan below 14th Street)
-- ============================================================
SELECT
    b.buildingid,
    b.full_address,
    b.boro,
    b.total_violations,
    ST_Y(b.geom::geometry) as latitude,
    ST_X(b.geom::geometry) as longitude
FROM buildings b
WHERE b.geom IS NOT NULL
  AND b.boro = 'MANHATTAN'
  AND ST_Within(
      b.geom::geometry,
      ST_MakeEnvelope(
          -74.05, 40.68,  -- Southwest corner
          -73.95, 40.75,  -- Northeast corner
          4326
      )
  )
ORDER BY b.total_violations DESC;


-- ============================================================
-- 6. Spatial join: violations near community facilities
--    (Self-join to find buildings close to each other)
-- ============================================================
WITH high_violation_buildings AS (
    SELECT
        buildingid,
        full_address,
        geom,
        total_violations
    FROM buildings
    WHERE geom IS NOT NULL
      AND total_violations >= 10
)
SELECT DISTINCT
    b1.buildingid as building_1,
    b1.full_address as address_1,
    b1.total_violations as violations_1,
    b2.buildingid as building_2,
    b2.full_address as address_2,
    b2.total_violations as violations_2,
    ROUND(
        ST_Distance(b1.geom::geography, b2.geom::geography)::numeric,
        2
    ) as distance_meters
FROM high_violation_buildings b1
CROSS JOIN high_violation_buildings b2
WHERE b1.buildingid < b2.buildingid  -- Avoid duplicates
  AND ST_DWithin(
      b1.geom::geography,
      b2.geom::geography,
      200  -- Within 200 meters
  )
ORDER BY distance_meters
LIMIT 50;


-- ============================================================
-- 7. Geospatial aggregation: average violations by distance from city center
--    (Manhattan center: 40.7589, -73.9851)
-- ============================================================
WITH distances AS (
    SELECT
        buildingid,
        full_address,
        total_violations,
        ROUND(
            ST_Distance(
                geom::geography,
                ST_SetSRID(ST_MakePoint(-73.9851, 40.7589), 4326)::geography
            ) / 1000.0,  -- Convert to km
            1
        ) as distance_from_center_km
    FROM buildings
    WHERE geom IS NOT NULL
),
distance_buckets AS (
    SELECT
        FLOOR(distance_from_center_km) as distance_bucket,
        COUNT(*) as building_count,
        AVG(total_violations) as avg_violations,
        SUM(total_violations) as total_violations
    FROM distances
    GROUP BY FLOOR(distance_from_center_km)
)
SELECT
    distance_bucket || '-' || (distance_bucket + 1) || ' km' as distance_range,
    building_count,
    ROUND(avg_violations, 2) as avg_violations_per_building,
    total_violations
FROM distance_buckets
WHERE distance_bucket <= 20  -- Within 20km of center
ORDER BY distance_bucket;


-- ============================================================
-- 8. Find geographic outliers (buildings far from others with violations)
-- ============================================================
WITH building_isolation AS (
    SELECT
        b.buildingid,
        b.full_address,
        b.boro,
        b.total_violations,
        b.geom,
        (
            SELECT MIN(ST_Distance(b.geom::geography, b2.geom::geography))
            FROM buildings b2
            WHERE b2.buildingid != b.buildingid
              AND b2.geom IS NOT NULL
              AND b2.total_violations > 0
        ) as distance_to_nearest_violation_building
    FROM buildings b
    WHERE b.geom IS NOT NULL
      AND b.total_violations > 0
)
SELECT
    buildingid,
    full_address,
    boro,
    total_violations,
    ROUND(distance_to_nearest_violation_building::numeric, 2) as meters_to_nearest,
    ST_Y(geom::geometry) as latitude,
    ST_X(geom::geometry) as longitude
FROM building_isolation
WHERE distance_to_nearest_violation_building > 1000  -- More than 1km away
ORDER BY distance_to_nearest_violation_building DESC
LIMIT 30;


-- ============================================================
-- 9. Create violation heat map grid (100m x 100m cells)
-- ============================================================
WITH grid AS (
    SELECT
        i,
        j,
        ST_MakeEnvelope(
            -74.05 + (i * 0.001),  -- ~100m longitude step
            40.68 + (j * 0.001),   -- ~100m latitude step
            -74.05 + ((i + 1) * 0.001),
            40.68 + ((j + 1) * 0.001),
            4326
        ) as cell
    FROM generate_series(0, 100) as i
    CROSS JOIN generate_series(0, 100) as j
),
violations_per_cell AS (
    SELECT
        g.i,
        g.j,
        g.cell,
        COUNT(v.violationid) as violation_count,
        ST_AsText(ST_Centroid(g.cell)) as cell_center
    FROM grid g
    LEFT JOIN violations v
        ON v.geom IS NOT NULL
        AND ST_Within(v.geom::geometry, g.cell)
    GROUP BY g.i, g.j, g.cell
)
SELECT
    i,
    j,
    violation_count,
    cell_center,
    CASE
        WHEN violation_count >= 50 THEN 'VERY HIGH'
        WHEN violation_count >= 20 THEN 'HIGH'
        WHEN violation_count >= 5 THEN 'MODERATE'
        WHEN violation_count > 0 THEN 'LOW'
        ELSE 'NONE'
    END as heat_level
FROM violations_per_cell
WHERE violation_count > 0
ORDER BY violation_count DESC
LIMIT 100;


-- ============================================================
-- 10. Calculate spatial autocorrelation: do high-violation buildings cluster?
--     (Simplified Moran's I approach)
-- ============================================================
WITH building_pairs AS (
    SELECT
        b1.buildingid as building_1,
        b1.total_violations as violations_1,
        b2.buildingid as building_2,
        b2.total_violations as violations_2,
        ST_Distance(b1.geom::geography, b2.geom::geography) as distance
    FROM buildings b1
    CROSS JOIN buildings b2
    WHERE b1.buildingid != b2.buildingid
      AND b1.geom IS NOT NULL
      AND b2.geom IS NOT NULL
      AND ST_DWithin(
          b1.geom::geography,
          b2.geom::geography,
          500  -- 500m neighborhood
      )
),
stats AS (
    SELECT
        AVG(total_violations) as mean_violations,
        STDDEV(total_violations) as std_violations
    FROM buildings
    WHERE total_violations > 0
)
SELECT
    AVG(
        ((violations_1 - mean_violations) / NULLIF(std_violations, 0)) *
        ((violations_2 - mean_violations) / NULLIF(std_violations, 0))
    ) as spatial_correlation_estimate
FROM building_pairs, stats
WHERE std_violations > 0;
