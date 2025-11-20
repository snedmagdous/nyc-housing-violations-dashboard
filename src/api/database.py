"""
Database Connection for FastAPI

This module provides database connectivity for the API.
It creates a "dependency" that FastAPI can inject into route functions.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config.database import DATABASE_URL

# Create SQLAlchemy engine
# Think of this as creating a connection pool to the database
# Instead of opening/closing connections constantly, we reuse them
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Checks if connection is alive before using
    echo=False  # Set to True to see all SQL queries (useful for debugging)
)

# Create a SessionLocal class
# Each instance will be a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit changes (we control when to save)
    autoflush=False,   # Don't auto-flush changes
    bind=engine        # Bind to our database engine
)


def get_db():
    """
    Dependency function that provides a database session.

    This is called by FastAPI for each request. It:
    1. Creates a new database session
    2. Yields it to the route function
    3. Closes it when done (even if there's an error)

    Usage in routes:
    @app.get("/api/violations")
    def get_violations(db: Session = Depends(get_db)):
        # db is automatically provided by FastAPI
        results = db.execute("SELECT * FROM violations LIMIT 10")
        return results
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the route
    finally:
        db.close()  # Always close when done


def test_db_connection():
    """
    Test if database connection works.
    Useful for debugging.
    """
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1;"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    print("Testing database connection...")
    if test_db_connection():
        print("[SUCCESS] Database connection successful!")
    else:
        print("[FAILED] Database connection failed!")
