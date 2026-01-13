"""
Data Fetching Module

Fetches housing violations data from NYC Open Data API.
"""

import os
from typing import Optional
import pandas as pd
from sodapy import Socrata
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fetch_hpd_violations(
    limit: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_path: str = "data/raw/hpd_violations.csv"
) -> pd.DataFrame:
    """
    Fetch HPD Housing Maintenance Code Violations from NYC Open Data.

    Parameters
    ----------
    limit : int, optional
        Maximum number of records to fetch. If None, fetches all records.
    start_date : str, optional
        Start date for filtering violations (format: YYYY-MM-DD)
    end_date : str, optional
        End date for filtering violations (format: YYYY-MM-DD)
    save_path : str
        Path to save the downloaded data

    Returns
    -------
    pd.DataFrame
        DataFrame containing violation records

    Examples
    --------
    >>> # Fetch last 1000 violations
    >>> df = fetch_hpd_violations(limit=1000)

    >>> # Fetch violations from 2023
    >>> df = fetch_hpd_violations(start_date="2023-01-01", end_date="2023-12-31")
    """

    # NYC Open Data domain and dataset identifier
    # HPD Violations: wvxf-dwi5
    domain = "data.cityofnewyork.us"
    dataset_id = "wvxf-dwi5"

    # App token for higher rate limits (optional but recommended)
    app_token = os.getenv("NYC_OPEN_DATA_TOKEN")

    print(f"Connecting to NYC Open Data API...")
    client = Socrata(domain, app_token)

    # Build query
    where_clause = []
    if start_date:
        where_clause.append(f"inspectiondate >= '{start_date}'")
    if end_date:
        where_clause.append(f"inspectiondate <= '{end_date}'")

    where_str = " AND ".join(where_clause) if where_clause else None

    print(f"Fetching violations data...")
    try:
        results = client.get(
            dataset_id,
            limit=limit,
            where=where_str,
            order="inspectiondate DESC"
        )

        df = pd.DataFrame.from_records(results)

        print(f"[OK] Fetched {len(df):,} violation records")

        # Save to CSV
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"[OK] Saved to {save_path}")

        return df

    except Exception as e:
        print(f"[ERROR] Error fetching data: {e}")
        raise
    finally:
        client.close()


def fetch_hpd_complaints(
    limit: Optional[int] = None,
    save_path: str = "data/raw/hpd_complaints.csv"
) -> pd.DataFrame:
    """
    Fetch HPD complaint data.

    Dataset ID: uwyv-629c
    """
    domain = "data.cityofnewyork.us"
    dataset_id = "uwyv-629c"
    app_token = os.getenv("NYC_OPEN_DATA_TOKEN")

    print(f"Fetching HPD complaints data...")
    client = Socrata(domain, app_token)

    try:
        results = client.get(dataset_id, limit=limit, order="receiveddate DESC")
        df = pd.DataFrame.from_records(results)

        print(f"[OK] Fetched {len(df):,} complaint records")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"[OK] Saved to {save_path}")

        return df

    finally:
        client.close()


if __name__ == "__main__":
    # Example usage: fetch recent violations
    print("=== NYC Housing Violations Data Fetcher ===\n")

    # Fetch a sample of recent violations (for testing)
    violations_df = fetch_hpd_violations(limit=100000)

    print(f"\nViolations DataFrame shape: {violations_df.shape}")
    print(f"\nColumns: {list(violations_df.columns)}")
    print(f"\nFirst few rows:")
    print(violations_df.head())
