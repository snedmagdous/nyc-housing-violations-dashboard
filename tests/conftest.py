"""
Pytest Configuration and Shared Fixtures

This file contains pytest configuration and fixtures that are shared
across all test files. Fixtures are reusable test components that
set up preconditions for tests.

Key Fixtures:
- client: FastAPI TestClient for making API requests in tests
- sample_violation_data: Mock violation data for testing
- sample_building_data: Mock building data for testing
- db_session: Mock database session for testing

Why use fixtures?
1. DRY (Don't Repeat Yourself) - Reuse setup code
2. Isolation - Each test gets fresh data
3. Cleanup - Fixtures handle teardown automatically
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime
import pandas as pd
import sys
import os

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# =================== API TESTING FIXTURES ===================

@pytest.fixture
def client():
    """
    Fixture that provides a FastAPI TestClient.

    This allows us to make HTTP requests to our API without actually
    running a server. It's perfect for integration testing.

    Usage in tests:
        def test_something(client):
            response = client.get("/api/violations")
            assert response.status_code == 200

    Why TestClient?
    - No need to run actual server
    - Tests run faster
    - Easy to mock database responses
    - Can test error conditions easily
    """
    from src.api.main import app

    # Create a test client
    # Important: This client automatically handles:
    # - Request/response serialization
    # - Cookie handling
    # - Redirects
    with TestClient(app) as test_client:
        yield test_client


# =================== DATA FIXTURES ===================

@pytest.fixture
def sample_violation_data():
    """
    Fixture providing sample violation data for testing.

    Returns a pandas DataFrame with realistic violation records.
    This is used for testing data cleaning, processing, and API responses.

    Edge Cases Covered:
    - Normal violations (Class A, B, C)
    - Open vs closed status
    - Various boroughs
    - Different date ranges
    - Missing values (apartment, story)
    - Special characters in addresses
    """
    data = {
        'violationid': [1, 2, 3, 4, 5],
        'buildingid': [101, 101, 102, 103, 104],
        'boro': ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND'],
        'housenumber': ['123', '456', '789', '321', '654'],
        'streetname': ['Main St', 'Oak Ave', 'Broadway', '5th Avenue', 'Victory Blvd'],
        'zip': ['10451', '11201', '10001', '11354', '10301'],
        'apartment': ['1A', None, '5B', None, '2C'],  # Some missing apartments
        'story': ['1', None, '5', '3', '2'],  # Some missing stories
        'class': ['A', 'B', 'C', 'I', 'A'],
        'inspectiondate': [
            '2023-01-15T00:00:00.000',
            '2023-02-20T00:00:00.000',
            '2023-03-10T00:00:00.000',
            '2023-04-05T00:00:00.000',
            '2023-05-12T00:00:00.000'
        ],
        'approveddate': [
            '2023-01-20T00:00:00.000',
            '2023-02-25T00:00:00.000',
            '2023-03-15T00:00:00.000',
            None,  # Not yet approved
            '2023-05-20T00:00:00.000'
        ],
        'currentstatus': [
            'VIOLATION DISMISSED',
            'VIOLATION OPEN',
            'VIOLATION OPEN',
            'VIOLATION OPEN',
            'VIOLATION DISMISSED'
        ],
        'currentstatusdate': [
            '2023-02-01T00:00:00.000',
            '2023-02-20T00:00:00.000',
            '2023-03-10T00:00:00.000',
            '2023-04-05T00:00:00.000',
            '2023-06-01T00:00:00.000'
        ],
        'novdescription': [
            'PAINT PEELING',
            'NO HEAT',
            'BROKEN WINDOW',
            'LEAKING PIPE',
            'MISSING SMOKE DETECTOR'
        ],
        'latitude': [40.8448, 40.6782, 40.7589, 40.7282, 40.5795],
        'longitude': [-73.8648, -73.9442, -73.9851, -73.7949, -74.1502],
        'rentimpairing': ['N', 'Y', 'Y', 'Y', 'N']
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_building_data():
    """
    Fixture providing sample building aggregation data.

    This represents the aggregated stats we calculate for each building.
    Used for testing building endpoints and aggregation logic.

    Edge Cases Covered:
    - Buildings with no violations
    - Buildings with only open violations
    - Buildings with mixed violation classes
    - High risk vs low risk buildings
    - Different boroughs
    """
    data = {
        'buildingid': [101, 102, 103, 104, 105],
        'boro': ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND'],
        'full_address': [
            '123 Main St, BRONX, NY 10451',
            '456 Oak Ave, BROOKLYN, NY 11201',
            '789 Broadway, MANHATTAN, NY 10001',
            '321 5th Avenue, QUEENS, NY 11354',
            '654 Victory Blvd, STATEN ISLAND, NY 10301'
        ],
        'zip': [10451, 11201, 10001, 11354, 10301],
        'latitude': [40.8448, 40.6782, 40.7589, 40.7282, 40.5795],
        'longitude': [-73.8648, -73.9442, -73.9851, -73.7949, -74.1502],
        'total_violations': [25, 12, 8, 3, 0],  # Including a building with 0 violations
        'open_violations': [5, 3, 0, 1, 0],
        'class_a_count': [10, 5, 3, 2, 0],
        'class_b_count': [8, 4, 3, 1, 0],
        'class_c_count': [5, 2, 1, 0, 0],
        'class_i_count': [2, 1, 1, 0, 0],
        'severe_violations': [13, 6, 4, 1, 0],  # B + C
        'risk_score': [85.5, 62.3, 45.1, 20.0, 0.0],
        'first_violation_date': [
            date(2020, 1, 15),
            date(2021, 3, 20),
            date(2022, 6, 10),
            date(2023, 1, 5),
            None  # No violations
        ],
        'most_recent_violation_date': [
            date(2023, 5, 20),
            date(2023, 4, 15),
            date(2023, 2, 28),
            date(2023, 1, 5),
            None  # No violations
        ]
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_raw_violation_csv(tmp_path):
    """
    Fixture that creates a temporary CSV file with raw violation data.

    This simulates the raw data downloaded from NYC Open Data API.
    Used for testing the data cleaning pipeline.

    Args:
        tmp_path: pytest fixture that provides a temporary directory

    Returns:
        Path to the temporary CSV file

    Why use tmp_path?
    - Creates actual files on disk for realistic testing
    - Automatically cleaned up after test
    - Each test gets its own isolated temp directory
    """
    csv_path = tmp_path / "raw_violations.csv"

    # Create raw data with issues that need cleaning
    raw_data = pd.DataFrame({
        'violationid': [1, 2, 2, 3],  # Includes a duplicate (id=2)
        'buildingid': [101, 102, 102, 103],
        'class': [' a ', 'B', ' b', 'C'],  # Mixed case, extra whitespace
        'housenumber': ['123 ', ' 456', '789', '321'],  # Whitespace issues
        'streetname': ['main st', 'OAK AVE', 'Broadway', '5th avenue'],  # Mixed case
        'boro': ['BRONX', 'brooklyn', 'MANHATTAN', 'QUEENS'],  # Mixed case
        'zip': ['10451', '11201', '11201', '11354'],
        'inspectiondate': [
            '2023-01-15T00:00:00.000',
            '2023-02-20T00:00:00.000',
            '2023-02-20T00:00:00.000',
            '2023-03-10T00:00:00.000'
        ],
        'currentstatus': ['VIOLATION OPEN', 'VIOLATION DISMISSED', 'VIOLATION DISMISSED', 'VIOLATION OPEN'],
        'latitude': [40.8448, 40.6782, 40.6782, 40.7282],
        'longitude': [-73.8648, -73.9442, -73.9442, -73.7949],
    })

    raw_data.to_csv(csv_path, index=False)
    return csv_path


# =================== DATABASE FIXTURES ===================

@pytest.fixture
def mock_db_session():
    """
    Fixture providing a mock database session.

    This is used when we want to test business logic without
    actually hitting the database.

    Why mock the database?
    - Tests run much faster
    - No need for test database setup
    - Can simulate error conditions (connection lost, etc.)
    - Tests are isolated and repeatable

    Note: This is a simple mock. For more complex scenarios,
    consider using SQLAlchemy's in-memory SQLite database.
    """
    from unittest.mock import MagicMock

    mock_session = MagicMock()

    # Configure the mock to return realistic values
    # Example: mock_session.execute().scalar() returns a number
    mock_session.execute.return_value.scalar.return_value = 100
    mock_session.execute.return_value.mappings.return_value.all.return_value = []

    return mock_session


# =================== PYTEST CONFIGURATION ===================

def pytest_configure(config):
    """
    Pytest hook that runs before all tests.

    Use this to set up test markers, configure logging, etc.

    Custom markers allow you to categorize tests:
        pytest -m unit      # Run only unit tests
        pytest -m slow      # Run only slow tests
        pytest -m "not slow"  # Run all except slow tests
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
