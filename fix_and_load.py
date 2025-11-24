"""
Quick script to fix constraints and complete buildings aggregation
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from config.database import get_engine

print("Fixing database constraints and completing data load...\n")

engine = get_engine()

with engine.begin() as conn:
    # Drop unique constraints AND indexes on BIN and BBL
    print("[1/3] Dropping unique constraints and indexes...")
    try:
        conn.execute(text("ALTER TABLE buildings DROP CONSTRAINT IF EXISTS buildings_bin_key;"))
        print("  + Dropped buildings_bin_key constraint")
    except:
        pass

    try:
        conn.execute(text("ALTER TABLE buildings DROP CONSTRAINT IF EXISTS buildings_bbl_key;"))
        print("  + Dropped buildings_bbl_key constraint")
    except:
        pass

    try:
        conn.execute(text("DROP INDEX IF EXISTS ix_buildings_bin;"))
        print("  + Dropped ix_buildings_bin index")
    except:
        pass

    try:
        conn.execute(text("DROP INDEX IF EXISTS ix_buildings_bbl;"))
        print("  + Dropped ix_buildings_bbl index")
    except:
        pass

    # Clear buildings table
    print("\n[2/3] Clearing buildings table...")
    conn.execute(text("TRUNCATE TABLE buildings;"))
    print("  + Cleared")

    # Aggregate buildings from violations
    print("\n[3/3] Aggregating buildings...")
    buildings_sql = """
    INSERT INTO buildings (
        buildingid,
        bin,
        bbl,
        boro,
        full_address,
        zip,
        nta,
        communityboard,
        latitude,
        longitude,
        geom,
        total_violations,
        open_violations,
        class_a_count,
        class_b_count,
        class_c_count,
        class_i_count,
        severe_violations,
        rent_impairing_violations,
        first_violation_date,
        most_recent_violation_date,
        risk_score
    )
    SELECT
        buildingid,
        MAX(bin) as bin,
        MAX(bbl) as bbl,
        MAX(boro) as boro,
        MAX(full_address) as full_address,
        MAX(zip) as zip,
        MAX(nta) as nta,
        MAX(communityboard) as communityboard,
        MAX(latitude) as latitude,
        MAX(longitude) as longitude,
        MAX(geom) as geom,
        COUNT(*) as total_violations,
        SUM(CASE WHEN is_open THEN 1 ELSE 0 END) as open_violations,
        SUM(CASE WHEN class = 'A' THEN 1 ELSE 0 END) as class_a_count,
        SUM(CASE WHEN class = 'B' THEN 1 ELSE 0 END) as class_b_count,
        SUM(CASE WHEN class = 'C' THEN 1 ELSE 0 END) as class_c_count,
        SUM(CASE WHEN class = 'I' THEN 1 ELSE 0 END) as class_i_count,
        SUM(CASE WHEN is_severe THEN 1 ELSE 0 END) as severe_violations,
        SUM(CASE WHEN is_rent_impairing THEN 1 ELSE 0 END) as rent_impairing_violations,
        MIN(inspectiondate) as first_violation_date,
        MAX(inspectiondate) as most_recent_violation_date,
        (
            SUM(CASE WHEN class = 'C' THEN 3 ELSE 0 END) +
            SUM(CASE WHEN class = 'B' THEN 2 ELSE 0 END) +
            SUM(CASE WHEN class = 'A' THEN 1 ELSE 0 END) +
            SUM(CASE WHEN is_open THEN 2 ELSE 0 END)
        )::float as risk_score
    FROM violations
    WHERE buildingid IS NOT NULL
    GROUP BY buildingid;
    """

    result = conn.execute(text(buildings_sql))
    building_count = result.rowcount
    print(f"  + Aggregated {building_count:,} buildings")

# Verify
print("\n[VERIFY] Final counts:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM violations;"))
    print(f"  + Violations: {result.fetchone()[0]:,}")

    result = conn.execute(text("SELECT COUNT(*) FROM buildings;"))
    print(f"  + Buildings: {result.fetchone()[0]:,}")

print("\n✓ Database loading complete!")
print("\nYour NYC Housing Violations database is ready for analysis!")
