"""
Data Cleaning Module

Cleans and preprocesses housing violations data.
"""

import pandas as pd
import numpy as np
import os
from typing import Optional
from datetime import datetime


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse date columns from ISO format strings to datetime objects.

    Converts: inspectiondate, approveddate, currentstatusdate
    """
    print("  > Parsing date columns...")

    date_columns = ['inspectiondate', 'approveddate', 'currentstatusdate']

    for col in date_columns:
        if col in df.columns:
            # Parse ISO format dates
            df[col] = pd.to_datetime(df[col], errors='coerce')
            print(f"    + Parsed {col}")

    return df


def standardize_violation_classes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize violation class values and add descriptions.

    Classes:
    - A: Non-hazardous
    - B: Hazardous
    - C: Immediately hazardous
    - I: Information orders
    """
    print("  > Standardizing violation classes...")

    # Ensure class is uppercase and stripped
    df['class'] = df['class'].str.strip().str.upper()

    # Map class to descriptions
    class_descriptions = {
        'A': 'Non-hazardous',
        'B': 'Hazardous',
        'C': 'Immediately hazardous',
        'I': 'Information order'
    }

    df['class_description'] = df['class'].map(class_descriptions)

    # Flag any unexpected classes
    unexpected_classes = df[~df['class'].isin(['A', 'B', 'C', 'I'])]['class'].unique()
    if len(unexpected_classes) > 0:
        print(f"    ! Warning: Found unexpected class values: {unexpected_classes}")

    print(f"    + Standardized {df['class'].nunique()} violation classes")

    return df


def clean_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize address components and create a full address field.
    """
    print("  > Cleaning addresses...")

    # Strip whitespace from address components
    df['housenumber'] = df['housenumber'].str.strip()
    df['streetname'] = df['streetname'].str.strip().str.title()
    df['boro'] = df['boro'].str.strip()

    # Create full address field
    df['full_address'] = (
        df['housenumber'].astype(str) + ' ' +
        df['streetname'].astype(str) + ', ' +
        df['boro'].astype(str) + ', NY ' +
        df['zip'].astype(str)
    )

    print(f"    + Created full_address field")

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values appropriately for each column type.
    """
    print("  > Handling missing values...")

    initial_missing = df.isnull().sum().sum()

    # Apartment and story are often legitimately missing (single-family homes, etc.)
    # Keep as NaN but document

    # For geospatial fields, we'll keep missing values
    # They can be imputed later if needed for specific analyses

    # Rentimpairing: fill missing with 'N' (assume not rent-impairing if not specified)
    if 'rentimpairing' in df.columns:
        df['rentimpairing'] = df['rentimpairing'].fillna('N')

    final_missing = df.isnull().sum().sum()
    print(f"    + Handled missing values (before: {initial_missing:,}, after: {final_missing:,})")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate violation records based on violation ID.
    """
    print("  > Removing duplicates...")

    initial_rows = len(df)

    # Remove duplicates based on violationid (should be unique)
    df = df.drop_duplicates(subset=['violationid'], keep='first')

    duplicates_removed = initial_rows - len(df)

    if duplicates_removed > 0:
        print(f"    + Removed {duplicates_removed:,} duplicate records")
    else:
        print(f"    + No duplicates found")

    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns for analysis.
    """
    print("  > Adding derived features...")

    # Extract year, month, day of week from inspection date
    if 'inspectiondate' in df.columns:
        df['inspection_year'] = df['inspectiondate'].dt.year
        df['inspection_month'] = df['inspectiondate'].dt.month
        df['inspection_month_name'] = df['inspectiondate'].dt.month_name()
        df['inspection_day_of_week'] = df['inspectiondate'].dt.day_name()
        df['inspection_quarter'] = df['inspectiondate'].dt.quarter

    # Calculate days from inspection to status change
    if 'inspectiondate' in df.columns and 'currentstatusdate' in df.columns:
        df['days_to_status_change'] = (
            df['currentstatusdate'] - df['inspectiondate']
        ).dt.days

    # Binary flags for easier filtering
    df['is_open'] = df['currentstatus'] == 'VIOLATION OPEN'
    df['is_severe'] = df['class'].isin(['B', 'C'])  # Hazardous or immediately hazardous
    df['is_rent_impairing'] = df['rentimpairing'] == 'Y'

    # Severity score (for ranking/sorting)
    severity_scores = {'A': 1, 'B': 2, 'C': 3, 'I': 0}
    df['severity_score'] = df['class'].map(severity_scores)

    print(f"    + Added temporal, binary, and severity features")

    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate cleaned data and flag potential issues.
    """
    print("  > Validating cleaned data...")

    issues = []

    # Check for valid coordinates
    if 'latitude' in df.columns and 'longitude' in df.columns:
        invalid_coords = df[
            (df['latitude'].notna()) &
            (df['longitude'].notna()) &
            ((df['latitude'] < 40.4) | (df['latitude'] > 41.0) |
             (df['longitude'] < -74.3) | (df['longitude'] > -73.7))
        ]
        if len(invalid_coords) > 0:
            issues.append(f"Found {len(invalid_coords)} records with coordinates outside NYC bounds")

    # Check for future dates
    today = pd.Timestamp.now()
    if 'inspectiondate' in df.columns:
        future_dates = df[df['inspectiondate'] > today]
        if len(future_dates) > 0:
            issues.append(f"Found {len(future_dates)} records with future inspection dates")

    # Check for negative days_to_status_change
    if 'days_to_status_change' in df.columns:
        negative_days = df[df['days_to_status_change'] < 0]
        if len(negative_days) > 0:
            issues.append(f"Found {len(negative_days)} records where status changed before inspection")

    if issues:
        print("    ! Validation warnings:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("    + All validation checks passed")

    return df


def clean_violations_data(
    input_path: str = "data/raw/hpd_violations.csv",
    output_path: str = "data/processed/violations_cleaned.csv"
) -> pd.DataFrame:
    """
    Clean and preprocess HPD violations data.

    Steps:
    1. Load raw data
    2. Parse dates
    3. Standardize violation classes
    4. Clean addresses
    5. Handle missing values
    6. Remove duplicates
    7. Add derived features
    8. Validate data

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

    print("=" * 60)
    print("NYC Housing Violations - Data Cleaning Pipeline")
    print("=" * 60)

    print(f"\n[1/8] Loading raw data from {input_path}...")
    df = pd.read_csv(input_path)

    initial_rows = len(df)
    initial_cols = len(df.columns)
    print(f"  > Loaded {initial_rows:,} rows × {initial_cols} columns")

    print(f"\n[2/8] Parsing dates...")
    df = parse_dates(df)

    print(f"\n[3/8] Standardizing violation classes...")
    df = standardize_violation_classes(df)

    print(f"\n[4/8] Cleaning addresses...")
    df = clean_addresses(df)

    print(f"\n[5/8] Handling missing values...")
    df = handle_missing_values(df)

    print(f"\n[6/8] Removing duplicates...")
    df = remove_duplicates(df)

    print(f"\n[7/8] Adding derived features...")
    df = add_derived_features(df)

    print(f"\n[8/8] Validating data...")
    df = validate_data(df)

    print("\n" + "=" * 60)
    print("Cleaning Summary")
    print("=" * 60)
    print(f"  Initial rows:     {initial_rows:,}")
    print(f"  Final rows:       {len(df):,}")
    print(f"  Rows removed:     {initial_rows - len(df):,}")
    print(f"  Initial columns:  {initial_cols}")
    print(f"  Final columns:    {len(df.columns)}")
    print(f"  Columns added:    {len(df.columns) - initial_cols}")

    # Display summary statistics
    print(f"\n  Violation class distribution:")
    for cls, count in df['class'].value_counts().sort_index().items():
        pct = (count / len(df)) * 100
        print(f"    Class {cls}: {count:,} ({pct:.1f}%)")

    print(f"\n  Status distribution:")
    for status, count in df['currentstatus'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"    {status}: {count:,} ({pct:.1f}%)")

    # Save cleaned data
    print(f"\n[SAVE] Saving cleaned data to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  + Saved successfully")

    print("\n" + "=" * 60)
    print("+ Data cleaning complete!")
    print("=" * 60)

    return df


if __name__ == "__main__":
    cleaned_df = clean_violations_data()

    print(f"\n[INFO] Cleaned data shape: {cleaned_df.shape}")
    print(f"[INFO] Ready for analysis!")
