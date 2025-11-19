"""
Database Configuration Module

Handles PostgreSQL connection and SQLAlchemy engine setup.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nyc_housing_violations')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Base for ORM models
Base = declarative_base()


def get_engine(echo=False):
    """
    Create and return a SQLAlchemy engine.

    Parameters
    ----------
    echo : bool
        If True, SQL queries will be logged to console

    Returns
    -------
    sqlalchemy.engine.Engine
        Database engine instance
    """
    return create_engine(
        DATABASE_URL,
        echo=echo,
        poolclass=NullPool,  # Disable connection pooling for simplicity
        connect_args={
            'connect_timeout': 10,
        }
    )


def get_session():
    """
    Create and return a database session.

    Returns
    -------
    sqlalchemy.orm.Session
        Database session instance
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def test_connection():
    """
    Test database connection and return status.

    Returns
    -------
    bool
        True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[OK] Connected to PostgreSQL")
            print(f"     Version: {version}")
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


def check_postgis():
    """
    Check if PostGIS extension is installed.

    Returns
    -------
    bool
        True if PostGIS is available, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT PostGIS_version();"))
            version = result.fetchone()[0]
            print(f"[OK] PostGIS extension found")
            print(f"     Version: {version}")
            return True
    except Exception as e:
        print(f"[WARNING] PostGIS not found: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Configuration Test")
    print("=" * 60)
    print(f"\nDatabase: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    print("\nTesting connection...")

    if test_connection():
        print("\nChecking PostGIS extension...")
        check_postgis()
    else:
        print("\n[ERROR] Please check your database configuration in .env file")
