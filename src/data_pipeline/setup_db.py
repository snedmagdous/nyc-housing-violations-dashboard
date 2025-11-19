"""
Database Setup Script

Creates PostgreSQL database schema with PostGIS support.
Defines tables: violations, buildings
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy import create_engine, text, Column, Integer, String, Float, Date, Boolean, BigInteger, Text
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geography
from config.database import get_engine, DATABASE_URL, test_connection, check_postgis

Base = declarative_base()


class Violation(Base):
    """
    Violations table schema.

    Stores individual housing code violation records with geospatial data.
    """
    __tablename__ = 'violations'

    # Primary key
    violationid = Column(BigInteger, primary_key=True, index=True)

    # Building identifiers
    buildingid = Column(BigInteger, index=True, nullable=False)
    registrationid = Column(BigInteger)
    bin = Column(BigInteger, index=True)  # Building Identification Number
    bbl = Column(BigInteger, index=True)  # Borough-Block-Lot

    # Location information
    boroid = Column(Integer)
    boro = Column(String(50), index=True)
    housenumber = Column(String(50))
    lowhousenumber = Column(String(50))
    highhousenumber = Column(String(50))
    streetname = Column(String(200))
    streetcode = Column(Integer)
    zip = Column(Integer, index=True)
    apartment = Column(String(50))
    story = Column(Float)
    block = Column(Integer)
    lot = Column(Integer)
    full_address = Column(Text)

    # Geospatial fields (PostGIS)
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geography('POINT', srid=4326), index=True)  # PostGIS geometry column

    # Administrative boundaries
    communityboard = Column(Integer, index=True)
    councildistrict = Column(Integer, index=True)
    censustract = Column(Integer)
    nta = Column(String(100), index=True)  # Neighborhood Tabulation Area

    # Violation details
    violation_class = Column(String(10), name='class', index=True)  # A, B, C, I
    class_description = Column(String(100))
    ordernumber = Column(Integer)
    novdescription = Column(Text, index=True)  # Notice of Violation description

    # Status and dates
    currentstatusid = Column(Integer)
    currentstatus = Column(String(100), index=True)
    violationstatus = Column(String(100))
    inspectiondate = Column(Date, index=True)
    approveddate = Column(Date)
    currentstatusdate = Column(Date)

    # Flags
    rentimpairing = Column(String(1))
    is_open = Column(Boolean, index=True)
    is_severe = Column(Boolean, index=True)
    is_rent_impairing = Column(Boolean)

    # Derived features
    inspection_year = Column(Integer, index=True)
    inspection_month = Column(Integer, index=True)
    inspection_month_name = Column(String(20))
    inspection_day_of_week = Column(String(20))
    inspection_quarter = Column(Integer)
    days_to_status_change = Column(Integer)
    severity_score = Column(Integer, index=True)


class Building(Base):
    """
    Buildings dimension table.

    Aggregated building-level metrics for faster queries.
    """
    __tablename__ = 'buildings'

    # Primary key
    buildingid = Column(BigInteger, primary_key=True, index=True)

    # Building identifiers
    bin = Column(BigInteger, unique=True, index=True)
    bbl = Column(BigInteger, unique=True, index=True)

    # Location
    boro = Column(String(50), index=True)
    full_address = Column(Text)
    zip = Column(Integer, index=True)
    nta = Column(String(100), index=True)
    communityboard = Column(Integer, index=True)

    # Geospatial
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geography('POINT', srid=4326), index=True)

    # Aggregated violation metrics
    total_violations = Column(Integer, default=0, index=True)
    open_violations = Column(Integer, default=0, index=True)
    class_a_count = Column(Integer, default=0)
    class_b_count = Column(Integer, default=0)
    class_c_count = Column(Integer, default=0)
    class_i_count = Column(Integer, default=0)
    severe_violations = Column(Integer, default=0, index=True)  # B + C
    rent_impairing_violations = Column(Integer, default=0)

    # Dates
    first_violation_date = Column(Date)
    most_recent_violation_date = Column(Date, index=True)

    # Risk score (for analysis)
    risk_score = Column(Float, index=True)


def create_postgis_extension(engine):
    """
    Enable PostGIS extension in the database.
    """
    print("\n[1/4] Enabling PostGIS extension...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            print("  + PostGIS extension enabled")
            return True
    except Exception as e:
        print(f"  ! Error enabling PostGIS: {e}")
        return False


def create_tables(engine):
    """
    Create all tables defined in Base metadata.
    """
    print("\n[2/4] Creating database tables...")
    try:
        Base.metadata.create_all(engine)
        print("  + Created 'violations' table")
        print("  + Created 'buildings' table")
        return True
    except Exception as e:
        print(f"  ! Error creating tables: {e}")
        return False


def create_indexes(engine):
    """
    Create additional custom indexes for performance.
    """
    print("\n[3/4] Creating additional indexes...")

    indexes = [
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_violations_boro_class ON violations(boro, class);",
        "CREATE INDEX IF NOT EXISTS idx_violations_year_month ON violations(inspection_year, inspection_month);",
        "CREATE INDEX IF NOT EXISTS idx_violations_status_date ON violations(currentstatus, inspectiondate);",
        "CREATE INDEX IF NOT EXISTS idx_buildings_boro_risk ON buildings(boro, risk_score DESC);",

        # Full-text search on violation descriptions (for NLP analysis later)
        "CREATE INDEX IF NOT EXISTS idx_violations_description_fts ON violations USING gin(to_tsvector('english', novdescription));",

        # Spatial indexes (automatically created for Geography columns, but being explicit)
        "CREATE INDEX IF NOT EXISTS idx_violations_geom ON violations USING GIST(geom);",
        "CREATE INDEX IF NOT EXISTS idx_buildings_geom ON buildings USING GIST(geom);",
    ]

    try:
        with engine.connect() as conn:
            for idx_sql in indexes:
                conn.execute(text(idx_sql))
            conn.commit()
        print("  + Created composite indexes")
        print("  + Created full-text search index")
        print("  + Created spatial indexes (GIST)")
        return True
    except Exception as e:
        print(f"  ! Error creating indexes: {e}")
        return False


def verify_schema(engine):
    """
    Verify that tables were created successfully.
    """
    print("\n[4/4] Verifying database schema...")

    try:
        with engine.connect() as conn:
            # Check violations table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'violations';"))
            violations_exists = result.fetchone()[0] == 1

            # Check buildings table
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'buildings';"))
            buildings_exists = result.fetchone()[0] == 1

            # Check PostGIS
            result = conn.execute(text("SELECT PostGIS_version();"))
            postgis_version = result.fetchone()[0]

            if violations_exists and buildings_exists:
                print("  + 'violations' table: EXISTS")
                print("  + 'buildings' table: EXISTS")
                print(f"  + PostGIS version: {postgis_version}")

                # Get column counts
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'violations';"))
                violations_cols = result.fetchone()[0]

                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'buildings';"))
                buildings_cols = result.fetchone()[0]

                print(f"  + 'violations' columns: {violations_cols}")
                print(f"  + 'buildings' columns: {buildings_cols}")

                return True
            else:
                print("  ! Some tables are missing")
                return False

    except Exception as e:
        print(f"  ! Error verifying schema: {e}")
        return False


def main():
    """
    Main setup function.
    """
    print("=" * 60)
    print("PostgreSQL Database Setup - NYC Housing Violations")
    print("=" * 60)

    # Test connection
    print("\n[SETUP] Testing database connection...")
    if not test_connection():
        print("\n[ERROR] Cannot connect to database.")
        print("Please ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database 'nyc_housing_violations' exists")
        print("  3. .env file has correct credentials")
        return False

    # Check PostGIS
    print("\n[SETUP] Checking PostGIS extension...")
    check_postgis()

    # Get engine
    engine = get_engine()

    # Create PostGIS extension
    if not create_postgis_extension(engine):
        return False

    # Create tables
    if not create_tables(engine):
        return False

    # Create indexes
    if not create_indexes(engine):
        return False

    # Verify
    if not verify_schema(engine):
        return False

    print("\n" + "=" * 60)
    print("+ Database setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python src/data_pipeline/load_data.py")
    print("  2. This will load your cleaned data into PostgreSQL")
    print("\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
