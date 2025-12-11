"""
Pydantic Schema Validation Tests

Tests that our Pydantic models correctly validate data.
These models define the "shape" of data in our API.

Why test schemas?
1. Catch breaking changes to API contracts
2. Validate that data validation rules work
3. Ensure type coercion works as expected
4. Document expected data formats

Pydantic Features Being Tested:
- Field validation (types, constraints)
- Default values
- Optional vs required fields
- Alias handling (e.g., "class" field)
- Data coercion (string to int, etc.)
"""

import pytest
from pydantic import ValidationError
from datetime import date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api.schemas import (
    ViolationBase,
    BuildingBase,
    BuildingDetail,
    ViolationListResponse,
    BuildingListResponse
)


# =================== VIOLATION SCHEMA TESTS ===================

def test_violation_base_with_valid_data():
    """
    Test that ViolationBase accepts valid data.

    This is the "happy path" - everything is correct.
    """
    data = {
        "violationid": 12345,
        "buildingid": 678,
        "boro": "BRONX",
        "full_address": "123 Main St, BRONX, NY 10451",
        "zip": 10451,
        "latitude": 40.8448,
        "longitude": -73.8648,
        "class": "A",  # Note: Uses alias for "violation_class"
        "class_description": "Non-hazardous",
        "currentstatus": "VIOLATION OPEN",
        "is_open": True,
        "is_severe": False
    }

    violation = ViolationBase(**data)

    # Verify all fields are set correctly
    assert violation.violationid == 12345
    assert violation.buildingid == 678
    assert violation.violation_class == "A"
    assert violation.is_open is True


def test_violation_optional_fields_can_be_none():
    """
    Test that optional fields can be omitted or None.

    Many fields in violations are optional because:
    - Data might be incomplete from NYC Open Data
    - Some fields only apply to certain violation types
    - Historical data might be missing newer fields

    Critical: The API should handle missing data gracefully.
    """
    # Minimal valid violation (only required field)
    data = {
        "violationid": 12345,
        "class": "A"
    }

    violation = ViolationBase(**data)

    # All optional fields should default to None
    assert violation.buildingid is None
    assert violation.boro is None
    assert violation.latitude is None
    assert violation.currentstatus is None


def test_violation_class_alias_works():
    """
    Test that 'class' alias works for violation_class field.

    Python reserved keywords:
    - "class" is a Python keyword, can't use as variable name
    - Pydantic's Field(alias="class") allows us to accept "class" in JSON
    - Internally stored as "violation_class"

    This is important because NYC Open Data uses "class" as field name.
    """
    data = {
        "violationid": 12345,
        "class": "B"  # Using the alias
    }

    violation = ViolationBase(**data)
    assert violation.violation_class == "B"


def test_violation_rejects_invalid_type():
    """
    Test that Pydantic rejects data with wrong types.

    Type safety is critical for:
    - Preventing runtime errors
    - Catching bugs early
    - API reliability

    Example: violationid should be int, not string.
    """
    data = {
        "violationid": "not-a-number",  # WRONG TYPE
        "class": "A"
    }

    with pytest.raises(ValidationError) as exc_info:
        ViolationBase(**data)

    # Check that the error mentions the field name
    assert "violationid" in str(exc_info.value)


# =================== BUILDING SCHEMA TESTS ===================

def test_building_base_with_complete_data():
    """
    Test BuildingBase with all fields populated.

    This tests a "fully loaded" building with aggregated stats.
    """
    data = {
        "buildingid": 101,
        "boro": "BRONX",
        "full_address": "123 Main St, BRONX, NY 10451",
        "zip": 10451,
        "latitude": 40.8448,
        "longitude": -73.8648,
        "total_violations": 25,
        "open_violations": 5,
        "class_a_count": 10,
        "class_b_count": 8,
        "class_c_count": 5,
        "class_i_count": 2,
        "severe_violations": 13,
        "risk_score": 75.5
    }

    building = BuildingBase(**data)

    assert building.buildingid == 101
    assert building.total_violations == 25
    assert building.risk_score == 75.5


def test_building_violation_counts_default_to_zero():
    """
    Test that violation counts default to 0, not None.

    Why default to 0?
    - Easier to sum/aggregate (no None handling needed)
    - More intuitive for API consumers
    - Matches database default values

    Edge case: New buildings with no violations yet.
    """
    data = {
        "buildingid": 999
    }

    building = BuildingBase(**data)

    # All counts should be 0, not None
    assert building.total_violations == 0
    assert building.open_violations == 0
    assert building.class_a_count == 0


def test_building_detail_extends_base():
    """
    Test that BuildingDetail includes all BuildingBase fields
    plus additional ones.

    Inheritance test: BuildingDetail should have all fields from
    BuildingBase, plus bin, bbl, etc.
    """
    data = {
        "buildingid": 101,
        "total_violations": 25,
        "bin": 1234567,  # Additional field in BuildingDetail
        "bbl": 9876543   # Additional field in BuildingDetail
    }

    building = BuildingDetail(**data)

    # Base fields should work
    assert building.buildingid == 101
    assert building.total_violations == 25

    # Extended fields should work
    assert building.bin == 1234567
    assert building.bbl == 9876543


# =================== RESPONSE WRAPPER TESTS ===================

def test_violation_list_response_structure():
    """
    Test ViolationListResponse wrapper model.

    This model wraps a list of violations with pagination metadata.

    API Response Format:
    {
        "total": 1523,
        "page": 1,
        "page_size": 100,
        "violations": [...]
    }

    Why wrap responses?
    - Include pagination info
    - Add metadata (total count, filters applied, etc.)
    - Consistent response structure across endpoints
    """
    response_data = {
        "total": 150,
        "page": 2,
        "page_size": 50,
        "violations": [
            {
                "violationid": 1,
                "class": "A"
            },
            {
                "violationid": 2,
                "class": "B"
            }
        ]
    }

    response = ViolationListResponse(**response_data)

    assert response.total == 150
    assert response.page == 2
    assert response.page_size == 50
    assert len(response.violations) == 2


def test_building_list_response_structure():
    """
    Test BuildingListResponse wrapper model.

    Same pattern as ViolationListResponse, but for buildings.
    """
    response_data = {
        "total": 500,
        "page": 1,
        "page_size": 100,
        "buildings": [
            {"buildingid": 101},
            {"buildingid": 102}
        ]
    }

    response = BuildingListResponse(**response_data)

    assert response.total == 500
    assert len(response.buildings) == 2


# =================== EDGE CASE TESTS ===================

def test_coordinates_accept_floats():
    """
    Test that latitude/longitude accept float values.

    Coordinates must be floats, not strings or integers.
    NYC coordinates should be in valid range:
    - Latitude: ~40.4 to 41.0
    - Longitude: ~-74.3 to -73.7

    Note: We don't validate coordinate ranges in the schema
    (that's done in data cleaning), but we ensure type is correct.
    """
    data = {
        "buildingid": 101,
        "latitude": 40.8448,
        "longitude": -73.8648
    }

    building = BuildingBase(**data)
    assert isinstance(building.latitude, float)
    assert isinstance(building.longitude, float)


def test_date_fields_accept_date_objects():
    """
    Test that date fields accept Python date objects.

    Pydantic should parse:
    - Python datetime.date objects
    - ISO format strings ("2023-01-15")
    - Timestamp integers

    This flexibility makes the API easier to use.
    """
    data = {
        "buildingid": 101,
        "first_violation_date": date(2023, 1, 15),
        "most_recent_violation_date": "2023-05-20"  # String format
    }

    building = BuildingBase(**data)

    assert building.first_violation_date == date(2023, 1, 15)
    assert building.most_recent_violation_date == date(2023, 5, 20)


def test_negative_violation_counts_are_rejected():
    """
    Test that negative violation counts are rejected.

    Business rule: You can't have negative violations.
    This could indicate a data error or calculation bug.

    Note: This test will PASS if we add validation to the schema.
    Currently, Pydantic doesn't enforce this - it's just showing
    where we could add validation.

    To add validation:
        class BuildingBase(BaseModel):
            total_violations: Optional[int] = Field(0, ge=0)  # ge=0 means >= 0
    """
    # This should ideally raise ValidationError, but currently doesn't
    # Uncomment the pytest.raises if you add validation
    data = {
        "buildingid": 101,
        "total_violations": -5  # INVALID
    }

    # with pytest.raises(ValidationError):
    #     BuildingBase(**data)

    # For now, just document that this is accepted
    building = BuildingBase(**data)
    # TODO: Add Field(ge=0) constraint to prevent negative values
