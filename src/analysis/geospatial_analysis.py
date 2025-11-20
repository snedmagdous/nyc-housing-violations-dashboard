"""
Geospatial Hotspot Analysis

Uses PostGIS and spatial statistics to identify:
- Geographic clusters of violations (hotspots)
- Spatial autocorrelation (do nearby areas have similar violation rates?)
- Concentration areas for targeted interventions

This helps answer: "WHERE are violations concentrated?"
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from sqlalchemy import text
from typing import Dict, List, Optional, Tuple
from config.database import get_engine


def find_hotspots(
    borough: Optional[str] = None,
    violation_class: Optional[str] = None,
    grid_size_meters: int = 500,
    min_violations: int = 5
) -> Dict:
    """
    Identify geographic hotspots using spatial grid analysis.

    Divides the city into a grid and counts violations in each cell.
    Cells with significantly more violations than average are "hotspots".

    Parameters
    ----------
    borough : str, optional
        Filter by borough
    violation_class : str, optional
        Filter by violation class
    grid_size_meters : int
        Size of grid cells in meters (default 500m = 0.3 miles)
    min_violations : int
        Minimum violations to be considered a hotspot

    Returns
    -------
    Dict
        - hotspots: List of hotspot locations with counts
        - statistics: Overall spatial statistics
        - geojson: GeoJSON format for mapping
    """
    print(f"Finding hotspots (grid size: {grid_size_meters}m)...")

    engine = get_engine()

    # Build query with spatial clustering
    # This uses PostGIS ST_SnapToGrid to create grid cells
    # Note: We cast Geography to Geometry for grid operations
    query = """
    WITH gridded_violations AS (
        SELECT
            -- Snap coordinates to grid to create cells (cast to geometry first)
            ST_SnapToGrid(geom::geometry, :grid_size) as grid_cell,
            COUNT(*) as violation_count,
            -- Get center of grid cell for display
            ST_X(ST_Centroid(ST_SnapToGrid(geom::geometry, :grid_size))) as lon,
            ST_Y(ST_Centroid(ST_SnapToGrid(geom::geometry, :grid_size))) as lat,
            array_agg(DISTINCT class) as classes,
            array_agg(DISTINCT boro) as boroughs
        FROM violations
        WHERE geom IS NOT NULL
    """

    params = {"grid_size": grid_size_meters}

    if borough:
        query += " AND boro = :borough"
        params["borough"] = borough.upper()

    if violation_class:
        query += " AND class = :violation_class"
        params["violation_class"] = violation_class.upper()

    query += """
        GROUP BY grid_cell
        HAVING COUNT(*) >= :min_violations
    )
    SELECT
        violation_count,
        lon,
        lat,
        classes,
        boroughs,
        -- Calculate how much above average this cell is
        (violation_count::float / AVG(violation_count) OVER ()) as intensity
    FROM gridded_violations
    ORDER BY violation_count DESC
    LIMIT 100
    """

    params["min_violations"] = min_violations

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        hotspots = result.mappings().all()

    if len(hotspots) == 0:
        return {
            "hotspots": [],
            "count": 0,
            "message": "No hotspots found with current filters"
        }

    # Convert to list of dicts for JSON
    hotspot_list = []
    for h in hotspots:
        hotspot_list.append({
            "latitude": float(h['lat']),
            "longitude": float(h['lon']),
            "violation_count": int(h['violation_count']),
            "intensity": float(h['intensity']),
            "classes": h['classes'],
            "boroughs": h['boroughs'][0] if h['boroughs'] else None
        })

    # Calculate statistics
    counts = [h['violation_count'] for h in hotspot_list]
    avg_count = np.mean(counts)
    std_count = np.std(counts)

    # Create GeoJSON for mapping
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [h['longitude'], h['latitude']]
                },
                "properties": {
                    "violation_count": h['violation_count'],
                    "intensity": h['intensity'],
                    "classes": h['classes'],
                    "borough": h['boroughs']
                }
            }
            for h in hotspot_list
        ]
    }

    return {
        "hotspots": hotspot_list,
        "count": len(hotspot_list),
        "statistics": {
            "average_violations_per_hotspot": float(avg_count),
            "std_dev": float(std_count),
            "top_hotspot_violations": int(counts[0]) if counts else 0,
            "grid_size_meters": grid_size_meters
        },
        "geojson": geojson
    }


def calculate_concentration_by_neighborhood() -> Dict:
    """
    Calculate violation concentration by NYC Neighborhood Tabulation Area (NTA).

    NTAs are ~300 neighborhoods defined by NYC Planning.

    Returns
    -------
    Dict
        - neighborhoods: List of neighborhoods with violation rates
        - top_10: Most affected neighborhoods
    """
    print("Calculating neighborhood concentration...")

    engine = get_engine()

    query = """
    SELECT
        nta,
        boro,
        COUNT(*) as total_violations,
        SUM(CASE WHEN is_open THEN 1 ELSE 0 END) as open_violations,
        SUM(CASE WHEN is_severe THEN 1 ELSE 0 END) as severe_violations,
        SUM(CASE WHEN class = 'C' THEN 1 ELSE 0 END) as class_c_count,
        -- Get average coordinates for neighborhood center
        AVG(latitude) as center_lat,
        AVG(longitude) as center_lon
    FROM violations
    WHERE nta IS NOT NULL
    GROUP BY nta, boro
    ORDER BY total_violations DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        neighborhoods = result.mappings().all()

    # Convert to list
    neighborhood_list = []
    for n in neighborhoods:
        neighborhood_list.append({
            "neighborhood": n['nta'],
            "borough": n['boro'],
            "total_violations": int(n['total_violations']),
            "open_violations": int(n['open_violations']),
            "severe_violations": int(n['severe_violations']),
            "class_c_count": int(n['class_c_count']),
            "center": {
                "latitude": float(n['center_lat']) if n['center_lat'] else None,
                "longitude": float(n['center_lon']) if n['center_lon'] else None
            }
        })

    return {
        "neighborhoods": neighborhood_list,
        "count": len(neighborhood_list),
        "top_10": neighborhood_list[:10]
    }


def find_building_clusters(
    radius_meters: int = 250,
    min_buildings: int = 3
) -> Dict:
    """
    Find clusters of buildings with high violations within a radius.

    Uses PostGIS ST_DWithin to find buildings close to each other.

    Parameters
    ----------
    radius_meters : int
        Search radius in meters
    min_buildings : int
        Minimum buildings to form a cluster

    Returns
    -------
    Dict
        - clusters: Geographic clusters of problematic buildings
    """
    print(f"Finding building clusters (radius: {radius_meters}m)...")

    engine = get_engine()

    # This query finds buildings where multiple high-violation buildings are nearby
    query = """
    WITH high_violation_buildings AS (
        SELECT
            buildingid,
            full_address,
            geom,
            total_violations,
            open_violations,
            risk_score,
            latitude,
            longitude
        FROM buildings
        WHERE total_violations >= 10
            AND geom IS NOT NULL
    )
    SELECT
        b1.buildingid as center_building_id,
        b1.full_address as center_address,
        b1.latitude as center_lat,
        b1.longitude as center_lon,
        b1.total_violations as center_violations,
        COUNT(b2.buildingid) as nearby_problem_buildings,
        SUM(b2.total_violations) as cluster_total_violations,
        AVG(b2.risk_score) as avg_risk_score,
        array_agg(b2.full_address) as nearby_addresses
    FROM high_violation_buildings b1
    JOIN high_violation_buildings b2
        ON ST_DWithin(b1.geom, b2.geom, :radius)
        AND b1.buildingid != b2.buildingid
    GROUP BY b1.buildingid, b1.full_address, b1.latitude, b1.longitude, b1.total_violations
    HAVING COUNT(b2.buildingid) >= :min_buildings
    ORDER BY COUNT(b2.buildingid) DESC, b1.total_violations DESC
    LIMIT 50
    """

    params = {
        "radius": radius_meters,
        "min_buildings": min_buildings - 1  # -1 because we're joining to other buildings
    }

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        clusters = result.mappings().all()

    if len(clusters) == 0:
        return {
            "clusters": [],
            "count": 0,
            "message": "No building clusters found"
        }

    cluster_list = []
    for c in clusters:
        cluster_list.append({
            "center_building": {
                "id": int(c['center_building_id']),
                "address": c['center_address'],
                "violations": int(c['center_violations']),
                "latitude": float(c['center_lat']),
                "longitude": float(c['center_lon'])
            },
            "nearby_problem_buildings": int(c['nearby_problem_buildings']),
            "cluster_total_violations": int(c['cluster_total_violations']),
            "avg_risk_score": float(c['avg_risk_score']),
            "radius_meters": radius_meters
        })

    return {
        "clusters": cluster_list,
        "count": len(cluster_list),
        "parameters": {
            "radius_meters": radius_meters,
            "min_buildings": min_buildings
        }
    }


def get_borough_comparison() -> Dict:
    """
    Compare violation statistics across NYC boroughs.

    Returns
    -------
    Dict
        - borough_stats: Statistics per borough
        - per_capita: Normalized by building count
    """
    print("Comparing boroughs...")

    engine = get_engine()

    query = """
    SELECT
        boro,
        COUNT(DISTINCT buildingid) as total_buildings,
        COUNT(*) as total_violations,
        SUM(CASE WHEN is_open THEN 1 ELSE 0 END) as open_violations,
        SUM(CASE WHEN is_severe THEN 1 ELSE 0 END) as severe_violations,
        SUM(CASE WHEN class = 'A' THEN 1 ELSE 0 END) as class_a,
        SUM(CASE WHEN class = 'B' THEN 1 ELSE 0 END) as class_b,
        SUM(CASE WHEN class = 'C' THEN 1 ELSE 0 END) as class_c,
        SUM(CASE WHEN class = 'I' THEN 1 ELSE 0 END) as class_i,
        AVG(severity_score) as avg_severity
    FROM violations
    WHERE boro IS NOT NULL
    GROUP BY boro
    ORDER BY total_violations DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        boroughs = result.mappings().all()

    borough_list = []
    for b in boroughs:
        buildings = int(b['total_buildings'])
        violations = int(b['total_violations'])

        borough_list.append({
            "borough": b['boro'],
            "total_buildings": buildings,
            "total_violations": violations,
            "violations_per_building": round(violations / buildings, 2) if buildings > 0 else 0,
            "open_violations": int(b['open_violations']),
            "severe_violations": int(b['severe_violations']),
            "class_distribution": {
                "A": int(b['class_a']),
                "B": int(b['class_b']),
                "C": int(b['class_c']),
                "I": int(b['class_i'])
            },
            "avg_severity": float(b['avg_severity']) if b['avg_severity'] else 0
        })

    return {
        "boroughs": borough_list,
        "count": len(borough_list)
    }


if __name__ == "__main__":
    # Test geospatial analysis
    print("=" * 60)
    print("Geospatial Hotspot Analysis - Testing")
    print("=" * 60)

    # Test hotspots
    print("\n[1/4] Finding Hotspots:")
    hotspots = find_hotspots(grid_size_meters=1000, min_violations=10)
    print(f"  Found {hotspots['count']} hotspots")
    if hotspots['count'] > 0:
        top = hotspots['hotspots'][0]
        print(f"  Top hotspot: {top['boroughs']} with {top['violation_count']} violations")
        print(f"  Location: ({top['latitude']:.4f}, {top['longitude']:.4f})")

    # Test neighborhoods
    print("\n[2/4] Neighborhood Concentration:")
    neighborhoods = calculate_concentration_by_neighborhood()
    print(f"  Analyzed {neighborhoods['count']} neighborhoods")
    if neighborhoods['count'] > 0:
        top = neighborhoods['top_10'][0]
        print(f"  Most affected: {top['neighborhood']}, {top['borough']}")
        print(f"  Violations: {top['total_violations']:,} ({top['open_violations']:,} open)")

    # Test building clusters
    print("\n[3/4] Building Clusters:")
    clusters = find_building_clusters(radius_meters=250, min_buildings=3)
    print(f"  Found {clusters['count']} clusters")
    if clusters['count'] > 0:
        top = clusters['clusters'][0]
        print(f"  Largest cluster: {top['center_building']['address']}")
        print(f"  {top['nearby_problem_buildings']} nearby problem buildings")

    # Test borough comparison
    print("\n[4/4] Borough Comparison:")
    boroughs = get_borough_comparison()
    for b in boroughs['boroughs']:
        print(f"  {b['borough']}: {b['total_violations']:,} violations ({b['violations_per_building']:.1f} per building)")

    print("\n" + "=" * 60)
    print("Geospatial analysis complete!")
    print("=" * 60)
