"""
Tests Package

This package contains all unit tests, integration tests, and API tests
for the NYC Housing Violations Dashboard.

Test Organization:
- test_api_*.py: API endpoint tests (FastAPI integration tests)
- test_data_*.py: Data pipeline and processing tests
- test_schemas.py: Pydantic model validation tests
- test_database.py: Database connection and query tests
- conftest.py: Shared pytest fixtures

Running Tests:
    # Run all tests
    pytest

    # Run with coverage
    pytest --cov=src --cov-report=html

    # Run specific test file
    pytest tests/test_api_health.py

    # Run specific test
    pytest tests/test_api_health.py::test_health_check_success

    # Run with verbose output
    pytest -v

    # Run and stop on first failure
    pytest -x
"""
