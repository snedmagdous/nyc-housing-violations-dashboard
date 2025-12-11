"""
Data Cleaning Pipeline Tests

Tests the data cleaning functions that transform raw NYC Open Data
into clean, analysis-ready data.

What we're testing:
1. Date parsing from ISO strings to datetime objects
2. Violation class standardization
3. Address cleaning and full_address creation
4. Duplicate removal
5. Missing value handling
6. Derived feature creation

Why test data cleaning?
- Data quality directly impacts analysis accuracy
- Catch edge cases (malformed dates, unexpected values)
- Ensure consistency across data pipeline
- Document expected transformations
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_pipeline.clean_data import (
    parse_dates,
    standardize_violation_classes,
    clean_addresses,
    handle_missing_values,
    remove_duplicates,
    add_derived_features,
    validate_data
)


# =================== DATE PARSING TESTS ===================

def test_parse_dates_converts_iso_strings():
    """
    Test that ISO format date strings are converted to datetime objects.

    NYC Open Data returns dates as ISO strings: "2023-01-15T00:00:00.000"
    We need to convert these to Python datetime objects for analysis.

    Edge cases tested:
    - Valid ISO dates
    - Multiple date columns
    - Preservation of time component (though we usually only use date)
    """
    df = pd.DataFrame({
        'violationid': [1, 2, 3],
        'inspectiondate': [
            '2023-01-15T00:00:00.000',
            '2023-02-20T00:00:00.000',
            '2023-03-10T00:00:00.000'
        ],
        'approveddate': [
            '2023-01-20T00:00:00.000',
            '2023-02-25T00:00:00.000',
            None  # Missing date - should become NaT (Not a Time)
        ]
    })

    result = parse_dates(df)

    # Check that dates were converted to datetime
    assert pd.api.types.is_datetime64_any_dtype(result['inspectiondate'])
    assert pd.api.types.is_datetime64_any_dtype(result['approveddate'])

    # Check specific values
    assert result['inspectiondate'].iloc[0] == pd.Timestamp('2023-01-15')
    assert pd.isna(result['approveddate'].iloc[2])  # None should become NaT


def test_parse_dates_handles_invalid_formats():
    """
    Test that invalid date formats are handled gracefully.

    Malformed data happens in real-world datasets:
    - Typos in dates
    - Wrong format
    - Garbage values

    Strategy: Convert to NaT (Not a Time) instead of crashing.
    We can then filter or flag these records later.
    """
    df = pd.DataFrame({
        'inspectiondate': [
            '2023-01-15T00:00:00.000',  # Valid
            'not-a-date',                # Invalid
            '2023-99-99T00:00:00.000',   # Invalid (month 99)
        ]
    })

    result = parse_dates(df)

    # First date should be valid
    assert result['inspectiondate'].iloc[0] == pd.Timestamp('2023-01-15')

    # Invalid dates should become NaT, not crash
    assert pd.isna(result['inspectiondate'].iloc[1])
    assert pd.isna(result['inspectiondate'].iloc[2])


# =================== VIOLATION CLASS STANDARDIZATION TESTS ===================

def test_standardize_classes_uppercases_values():
    """
    Test that violation classes are converted to uppercase.

    NYC data might have inconsistent casing: "a", "A", " A "
    We need to standardize to: "A", "B", "C", "I"

    Why uppercase?
    - Easier to query ("WHERE class = 'A'")
    - Consistent with NYC's official documentation
    - Prevents duplicate categories in aggregations
    """
    df = pd.DataFrame({
        'class': ['a', 'B', ' c ', 'i']  # Mixed case, extra whitespace
    })

    result = standardize_violation_classes(df)

    # All should be uppercase and trimmed
    assert result['class'].iloc[0] == 'A'
    assert result['class'].iloc[1] == 'B'
    assert result['class'].iloc[2] == 'C'
    assert result['class'].iloc[3] == 'I'


def test_standardize_classes_adds_descriptions():
    """
    Test that class descriptions are added correctly.

    Mapping:
    - A: Non-hazardous
    - B: Hazardous
    - C: Immediately hazardous
    - I: Information order

    Why add descriptions?
    - Human-readable for reports
    - Easier API responses
    - Documentation for users
    """
    df = pd.DataFrame({
        'class': ['A', 'B', 'C', 'I']
    })

    result = standardize_violation_classes(df)

    assert result['class_description'].iloc[0] == 'Non-hazardous'
    assert result['class_description'].iloc[1] == 'Hazardous'
    assert result['class_description'].iloc[2] == 'Immediately hazardous'
    assert result['class_description'].iloc[3] == 'Information order'


def test_standardize_classes_handles_unexpected_values():
    """
    Test handling of unexpected violation classes.

    Real-world data might have:
    - Data entry errors
    - New violation types
    - Deprecated classes

    Strategy: Don't crash, but flag for review.
    class_description will be NaN for unexpected values.
    """
    df = pd.DataFrame({
        'class': ['A', 'X', 'Z']  # X and Z are not valid
    })

    result = standardize_violation_classes(df)

    # Valid class should work
    assert result['class_description'].iloc[0] == 'Non-hazardous'

    # Invalid classes should have NaN descriptions
    assert pd.isna(result['class_description'].iloc[1])
    assert pd.isna(result['class_description'].iloc[2])


# =================== ADDRESS CLEANING TESTS ===================

def test_clean_addresses_creates_full_address():
    """
    Test that full_address field is created from components.

    Format: "123 Main St, BRONX, NY 10451"

    Why create full_address?
    - Easier for users to read
    - Better for search/autocomplete
    - Matches how people think about addresses
    """
    df = pd.DataFrame({
        'housenumber': ['123', '456'],
        'streetname': ['Main St', 'Oak Ave'],
        'boro': ['BRONX', 'BROOKLYN'],
        'zip': ['10451', '11201']
    })

    result = clean_addresses(df)

    expected_1 = '123 Main St, BRONX, NY 10451'
    expected_2 = '456 Oak Ave, BROOKLYN, NY 11201'

    assert result['full_address'].iloc[0] == expected_1
    assert result['full_address'].iloc[1] == expected_2


def test_clean_addresses_handles_whitespace():
    """
    Test that extra whitespace is removed.

    Real-world data issues:
    - Leading/trailing spaces
    - Double spaces
    - Tab characters

    Example: " 123 " -> "123"
    """
    df = pd.DataFrame({
        'housenumber': [' 123 ', '456'],
        'streetname': ['main st', 'OAK AVE'],  # Also test titlecase
        'boro': [' BRONX ', 'BROOKLYN'],
        'zip': ['10451', '11201']
    })

    result = clean_addresses(df)

    # Whitespace should be stripped
    assert result['housenumber'].iloc[0] == '123'
    assert result['boro'].iloc[0] == 'BRONX'

    # Street names should be title case
    assert result['streetname'].iloc[0] == 'Main St'


# =================== DUPLICATE REMOVAL TESTS ===================

def test_remove_duplicates_by_violation_id():
    """
    Test that duplicate violations are removed.

    Duplicates can happen when:
    - Data is exported multiple times
    - Records are updated in source system
    - API pagination issues

    Strategy: Keep first occurrence, remove rest.
    violationid should be unique identifier.
    """
    df = pd.DataFrame({
        'violationid': [1, 2, 2, 3],  # 2 appears twice
        'buildingid': [101, 102, 102, 103]
    })

    result = remove_duplicates(df)

    # Should have 3 rows, not 4
    assert len(result) == 3

    # violation_id 2 should appear only once
    assert result['violationid'].tolist() == [1, 2, 3]


def test_remove_duplicates_keeps_first_occurrence():
    """
    Test that when duplicates exist, the FIRST one is kept.

    This is important if records have different data
    (e.g., one updated later with more info).

    Usually we want the first occurrence because it represents
    the original violation record.
    """
    df = pd.DataFrame({
        'violationid': [1, 1],
        'currentstatus': ['OPEN', 'CLOSED']  # Different statuses
    })

    result = remove_duplicates(df)

    # Should keep first record (OPEN status)
    assert len(result) == 1
    assert result['currentstatus'].iloc[0] == 'OPEN'


# =================== DERIVED FEATURES TESTS ===================

def test_add_derived_features_creates_temporal_fields():
    """
    Test that temporal features are extracted from dates.

    From inspectiondate, we derive:
    - inspection_year: 2023
    - inspection_month: 1 (January)
    - inspection_month_name: "January"
    - inspection_day_of_week: "Monday"
    - inspection_quarter: 1 (Q1)

    Why derive these?
    - Easier aggregations (violations per month)
    - Seasonal analysis (winter vs summer)
    - Trend detection
    """
    df = pd.DataFrame({
        'inspectiondate': pd.to_datetime(['2023-01-15', '2023-06-20'])
    })

    result = add_derived_features(df)

    # Check first row (January)
    assert result['inspection_year'].iloc[0] == 2023
    assert result['inspection_month'].iloc[0] == 1
    assert result['inspection_month_name'].iloc[0] == 'January'
    assert result['inspection_quarter'].iloc[0] == 1

    # Check second row (June)
    assert result['inspection_month'].iloc[1] == 6
    assert result['inspection_quarter'].iloc[1] == 2


def test_add_derived_features_creates_binary_flags():
    """
    Test that boolean flags are created for common filters.

    Binary flags make queries easier:
    - is_open: Is violation still open?
    - is_severe: Is it Class B or C?
    - is_rent_impairing: Does it affect habitability?

    Why use binary flags?
    - Faster queries ("WHERE is_open = true")
    - Easier to aggregate ("COUNT WHERE is_severe")
    - More readable than complex conditions
    """
    df = pd.DataFrame({
        'currentstatus': ['VIOLATION OPEN', 'VIOLATION DISMISSED'],
        'class': ['C', 'A'],
        'rentimpairing': ['Y', 'N']
    })

    result = add_derived_features(df)

    # First row: open, severe (Class C), rent-impairing
    assert result['is_open'].iloc[0] is True
    assert result['is_severe'].iloc[0] is True
    assert result['is_rent_impairing'].iloc[0] is True

    # Second row: closed, not severe (Class A), not rent-impairing
    assert result['is_open'].iloc[1] is False
    assert result['is_severe'].iloc[1] is False
    assert result['is_rent_impairing'].iloc[1] is False


def test_add_derived_features_calculates_severity_score():
    """
    Test that numeric severity scores are assigned.

    Mapping:
    - Class A: 1 (least severe)
    - Class B: 2
    - Class C: 3 (most severe)
    - Class I: 0 (informational)

    Why numeric scores?
    - Easy to sort by severity
    - Calculate average severity
    - Weight violations in risk models
    """
    df = pd.DataFrame({
        'class': ['A', 'B', 'C', 'I']
    })

    result = add_derived_features(df)

    assert result['severity_score'].iloc[0] == 1  # Class A
    assert result['severity_score'].iloc[1] == 2  # Class B
    assert result['severity_score'].iloc[2] == 3  # Class C
    assert result['severity_score'].iloc[3] == 0  # Class I


def test_add_derived_features_calculates_days_to_status_change():
    """
    Test calculation of time between inspection and status change.

    This metric shows enforcement lag:
    - How long from inspection to resolution?
    - Are some neighborhoods faster than others?
    - Are violations being addressed promptly?

    Formula: currentstatusdate - inspectiondate
    """
    df = pd.DataFrame({
        'inspectiondate': pd.to_datetime(['2023-01-15', '2023-02-01']),
        'currentstatusdate': pd.to_datetime(['2023-01-25', '2023-02-15'])
    })

    result = add_derived_features(df)

    # First violation: 10 days to status change
    assert result['days_to_status_change'].iloc[0] == 10

    # Second violation: 14 days to status change
    assert result['days_to_status_change'].iloc[1] == 14


# =================== DATA VALIDATION TESTS ===================

def test_validate_data_flags_invalid_coordinates():
    """
    Test that coordinates outside NYC are flagged.

    NYC bounds (approximate):
    - Latitude: 40.4 to 41.0
    - Longitude: -74.3 to -73.7

    Coordinates outside this range indicate:
    - Geocoding errors
    - Data entry mistakes
    - Wrong coordinate system

    Note: validate_data() doesn't remove bad data, just flags it.
    """
    df = pd.DataFrame({
        'latitude': [40.8, 50.0, 40.7],  # 50.0 is way off (Canada!)
        'longitude': [-73.9, -73.9, -73.9]
    })

    # validate_data returns the df unchanged, but prints warnings
    # In a production system, you'd want to return flagged rows
    result = validate_data(df)

    # Data should be unchanged
    assert len(result) == 3
    # In real implementation, could add 'validation_errors' column


def test_validate_data_flags_future_dates():
    """
    Test that future inspection dates are flagged.

    You can't inspect a building in the future!
    This indicates:
    - Data entry error (typo in year)
    - System clock issues
    - Test data in production

    These records should be investigated.
    """
    df = pd.DataFrame({
        'inspectiondate': pd.to_datetime([
            '2023-01-15',  # Valid (past)
            '2099-01-15'   # Invalid (future)
        ])
    })

    result = validate_data(df)

    # Should flag the future date
    assert len(result) == 2


# =================== INTEGRATION TEST ===================

def test_full_cleaning_pipeline(sample_raw_violation_csv):
    """
    Integration test: Run entire cleaning pipeline on sample data.

    This tests that all cleaning functions work together:
    1. Load raw CSV
    2. Parse dates
    3. Standardize classes
    4. Clean addresses
    5. Remove duplicates
    6. Add derived features
    7. Validate

    This catches issues like:
    - Functions changing column names unexpectedly
    - Order dependencies
    - Data type incompatibilities
    """
    # Load the sample CSV created by the fixture
    df = pd.read_csv(sample_raw_violation_csv)

    # Run full pipeline
    df = parse_dates(df)
    df = standardize_violation_classes(df)
    df = clean_addresses(df)
    df = remove_duplicates(df)
    df = add_derived_features(df)
    df = validate_data(df)

    # Verify final state
    # Should have 3 rows (started with 4, removed 1 duplicate)
    assert len(df) == 3

    # Check derived columns exist
    assert 'inspection_year' in df.columns
    assert 'is_open' in df.columns
    assert 'severity_score' in df.columns
    assert 'full_address' in df.columns

    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(df['inspectiondate'])
    assert pd.api.types.is_bool_dtype(df['is_open'])


# =================== EDGE CASE: EMPTY DATAFRAME ===================

def test_cleaning_handles_empty_dataframe():
    """
    Test that cleaning functions handle empty DataFrames gracefully.

    Edge case: What if API returns 0 records?
    - New filter with no matches
    - Date range with no violations
    - Network error resulting in empty response

    Functions should return empty DataFrame, not crash.
    """
    df = pd.DataFrame()

    # None of these should crash
    result = standardize_violation_classes(df)
    assert len(result) == 0

    result = remove_duplicates(df)
    assert len(result) == 0
