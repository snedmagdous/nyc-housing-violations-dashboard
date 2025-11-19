"""
Data Loading Module

Loads cleaned data into PostgreSQL database with PostGIS support.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from geoalchemy2 import WKTElement
from tqdm import tqdm
from config.database import get_engine, test_connection


def prepare_violations_data(df):
    """
    Prepare violations dataframe for database loading.

    - Convert dates to proper format
    - Create PostGIS geometry from lat/long
    - Rename columns to match schema
    """
    print("  > Preparing violations data...")

    df = df.copy()

    # Parse dates
    date_cols = ['inspectiondate', 'approveddate', 'currentstatusdate']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Rename 'class' column to 'violation_class' (class is reserved keyword)
    if 'class' in df.columns:
        df['violation_class'] = df['class']
        df = df.drop(columns=['class'])

    # Create PostGIS geometry (WKT format: POINT(longitude latitude))
    # Only for records with valid coordinates
    def create_point_wkt(row):
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            return f'POINT({row["longitude"]} {row["latitude"]})'
        return None

    df['geom'] = df.apply(create_point_wkt, axis=1)

    # Convert boolean columns (pandas bool to PostgreSQL boolean)
    bool_cols = ['is_open', 'is_severe', 'is_rent_impairing']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    print(f"    + Prepared {len(df):,} violation records")

    return df


def load_violations(engine, csv_path='data/processed/violations_cleaned.csv', batch_size=1000):
    """
    Load violations data into PostgreSQL.
    """
    print("\n[1/2] Loading violations table...")

    # Read CSV
    print("  > Reading CSV file...")
    df = pd.read_csv(csv_path)
    print(f"    + Read {len(df):,} records")

    # Prepare data
    df = prepare_violations_data(df)

    # Load in batches with progress bar
    print(f"  > Loading to database (batch size: {batch_size})...")

    total_rows = len(df)
    num_batches = (total_rows + batch_size - 1) // batch_size

    with engine.begin() as conn:
        # Clear existing data
        conn.execute(text("TRUNCATE TABLE violations;"))

        for i in tqdm(range(num_batches), desc="  Loading batches"):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]

            # Convert geometry column for PostGIS
            batch_data = batch.copy()
            if 'geom' in batch_data.columns:
                batch_data['geom'] = batch_data['geom'].apply(
                    lambda x: WKTElement(x, srid=4326) if x else None
                )

            # Load batch
            batch_data.to_sql(
                'violations',
                conn,
                if_exists='append',
                index=False,
                method='multi'
            )

    print(f"    + Loaded {total_rows:,} violations")

    return total_rows


def aggregate_buildings(engine):
    """
    Aggregate violations data to create buildings dimension table.

    Uses SQL for efficient aggregation.
    """
    print("\n[2/2] Aggregating buildings table...")

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
        SUM(CASE WHEN violation_class = 'A' THEN 1 ELSE 0 END) as class_a_count,
        SUM(CASE WHEN violation_class = 'B' THEN 1 ELSE 0 END) as class_b_count,
        SUM(CASE WHEN violation_class = 'C' THEN 1 ELSE 0 END) as class_c_count,
        SUM(CASE WHEN violation_class = 'I' THEN 1 ELSE 0 END) as class_i_count,
        SUM(CASE WHEN is_severe THEN 1 ELSE 0 END) as severe_violations,
        SUM(CASE WHEN is_rent_impairing THEN 1 ELSE 0 END) as rent_impairing_violations,
        MIN(inspectiondate) as first_violation_date,
        MAX(inspectiondate) as most_recent_violation_date,
        -- Simple risk score: weighted by severity and open status
        (
            SUM(CASE WHEN violation_class = 'C' THEN 3 ELSE 0 END) +
            SUM(CASE WHEN violation_class = 'B' THEN 2 ELSE 0 END) +
            SUM(CASE WHEN violation_class = 'A' THEN 1 ELSE 0 END) +
            SUM(CASE WHEN is_open THEN 2 ELSE 0 END)
        )::float as risk_score
    FROM violations
    WHERE buildingid IS NOT NULL
    GROUP BY buildingid
    ON CONFLICT (buildingid) DO UPDATE SET
        total_violations = EXCLUDED.total_violations,
        open_violations = EXCLUDED.open_violations,
        class_a_count = EXCLUDED.class_a_count,
        class_b_count = EXCLUDED.class_b_count,
        class_c_count = EXCLUDED.class_c_count,
        class_i_count = EXCLUDED.class_i_count,
        severe_violations = EXCLUDED.severe_violations,
        rent_impairing_violations = EXCLUDED.rent_impairing_violations,
        first_violation_date = EXCLUDED.first_violation_date,
        most_recent_violation_date = EXCLUDED.most_recent_violation_date,
        risk_score = EXCLUDED.risk_score;
    """

    try:
        with engine.begin() as conn:
            # Clear existing data
            conn.execute(text("TRUNCATE TABLE buildings;"))

            # Aggregate
            result = conn.execute(text(buildings_sql))
            building_count = result.rowcount

        print(f"    + Aggregated {building_count:,} buildings")
        return building_count

    except Exception as e:
        print(f"    ! Error aggregating buildings: {e}")
        return 0


def verify_load(engine):
    """
    Verify data was loaded correctly.
    """
    print("\n[VERIFY] Checking data integrity...")

    try:
        with engine.connect() as conn:
            # Count violations
            result = conn.execute(text("SELECT COUNT(*) FROM violations;"))
            violations_count = result.fetchone()[0]

            # Count buildings
            result = conn.execute(text("SELECT COUNT(*) FROM buildings;"))
            buildings_count = result.fetchone()[0]

            # Count violations with geometry
            result = conn.execute(text("SELECT COUNT(*) FROM violations WHERE geom IS NOT NULL;"))
            geom_count = result.fetchone()[0]

            # Sample violation classes
            result = conn.execute(text("""
                SELECT violation_class, COUNT(*) as count
                FROM violations
                GROUP BY violation_class
                ORDER BY violation_class;
            """))
            class_dist = result.fetchall()

            print(f"    + Violations: {violations_count:,}")
            print(f"    + Buildings: {buildings_count:,}")
            print(f"    + Records with geometry: {geom_count:,} ({geom_count/violations_count*100:.1f}%)")
            print(f"    + Violation class distribution:")
            for cls, count in class_dist:
                print(f"      - Class {cls}: {count:,}")

            return True

    except Exception as e:
        print(f"    ! Error verifying data: {e}")
        return False


def main():
    """
    Main data loading pipeline.
    """
    print("=" * 60)
    print("Load Data to PostgreSQL - NYC Housing Violations")
    print("=" * 60)

    # Test connection
    print("\n[SETUP] Testing database connection...")
    if not test_connection():
        print("\n[ERROR] Cannot connect to database.")
        print("Please run: python src/data_pipeline/setup_db.py")
        return False

    # Get engine
    engine = get_engine()

    # Load violations
    violations_loaded = load_violations(engine)

    if violations_loaded == 0:
        print("\n[ERROR] No violations loaded. Exiting.")
        return False

    # Aggregate buildings
    buildings_loaded = aggregate_buildings(engine)

    # Verify
    verify_load(engine)

    print("\n" + "=" * 60)
    print("+ Data loading complete!")
    print("=" * 60)
    print("\nDatabase is ready for analysis!")
    print("Run SQL queries from: sql_queries/")
    print("\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
