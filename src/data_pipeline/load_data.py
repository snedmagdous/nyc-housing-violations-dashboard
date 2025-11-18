"""
Data Loading Module

Loads cleaned data into PostgreSQL database.
"""

import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()


def load_to_database(
    csv_path: str = "data/processed/violations_cleaned.csv",
    table_name: str = "violations"
) -> None:
    """
    Load cleaned violations data to PostgreSQL.

    Parameters
    ----------
    csv_path : str
        Path to cleaned violations CSV
    table_name : str
        Name of the database table
    """

    # Get database connection string from environment
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("⚠ Warning: DATABASE_URL not set. Skipping database load.")
        print("  Set DATABASE_URL in .env file to enable database functionality.")
        return

    print(f"Loading data to PostgreSQL...")
    df = pd.read_csv(csv_path)

    # Create database engine
    engine = create_engine(db_url)

    # Load to database
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",  # or 'append' for incremental loads
        index=False,
        method="multi",
        chunksize=1000
    )

    print(f"✓ Loaded {len(df):,} rows to table '{table_name}'")


if __name__ == "__main__":
    load_to_database()
