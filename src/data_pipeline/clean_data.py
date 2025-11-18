"""
Data Cleaning Module

Cleans and preprocesses housing violations data.
"""

import pandas as pd
import numpy as np
from typing import Optional


def clean_violations_data(
    input_path: str = "data/raw/hpd_violations.csv",
    output_path: str = "data/processed/violations_cleaned.csv"
) -> pd.DataFrame:
    """
    Clean and preprocess HPD violations data.

    Steps:
    1. Load raw data
    2. Handle missing values
    3. Standardize data types
    4. Parse dates
    5. Clean addresses
    6. Remove duplicates
    7. Add derived columns

    Parameters
    ----------
    input_path : str
        Path to raw violations CSV
    output_path : str
        Path to save cleaned data

    Returns
    -------
    pd.DataFrame
        Cleaned violations data
    """

    print(f"Loading raw data from {input_path}...")
    df = pd.read_csv(input_path)

    initial_rows = len(df)
    print(f"Initial rows: {initial_rows:,}")

    # TODO: Implement cleaning steps
    # - Parse dates (inspectiondate, originalcertifybydate, etc.)
    # - Standardize violation classes (A, B, C)
    # - Clean addresses
    # - Handle missing values
    # - Remove duplicates
    # - Add derived features

    print(f"✓ Cleaning complete. Final rows: {len(df):,}")

    # Save cleaned data
    df.to_csv(output_path, index=False)
    print(f"✓ Saved to {output_path}")

    return df


if __name__ == "__main__":
    cleaned_df = clean_violations_data()
    print(f"\nCleaned data shape: {cleaned_df.shape}")
