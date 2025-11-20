"""
Pydantic Models (Schemas) for API

These models define the SHAPE of data that goes in/out of the API.
Think of them as contracts: "This is what a Violation looks like"

Why use Pydantic?
1. Automatic validation - FastAPI checks incoming data matches the schema
2. Auto-documentation - Shows up in /docs
3. Type safety - Catch errors early
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ViolationBase(BaseModel):
    """
    Base model for a violation.

    This defines what a violation looks like when returned from the API.
    Example JSON response:
    {
        "violationid": 18405284,
        "buildingid": 85470,
        "boro": "BRONX",
        "full_address": "1163 Hoe Avenue, BRONX, NY 10459",
        "class": "A",
        "class_description": "Non-hazardous",
        ...
    }
    """
    violationid: int
    buildingid: Optional[int] = None

    # Location info
    boro: Optional[str] = None
    full_address: Optional[str] = None
    zip: Optional[int] = None
    nta: Optional[str] = Field(None, description="Neighborhood Tabulation Area")

    # Coordinates for mapping
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Violation details
    violation_class: str = Field(alias="class", description="A, B, C, or I")
    class_description: Optional[str] = None
    novdescription: Optional[str] = Field(None, description="Violation description")

    # Status and dates
    currentstatus: Optional[str] = None
    inspectiondate: Optional[date] = None

    # Flags
    is_open: Optional[bool] = None
    is_severe: Optional[bool] = None
    severity_score: Optional[int] = None

    class Config:
        # This allows the model to read from database column names
        # even if they don't match Python naming conventions
        orm_mode = True
        populate_by_name = True


class ViolationDetail(ViolationBase):
    """
    Extended violation model with ALL fields.
    Use this when user requests full details of a specific violation.
    """
    registrationid: Optional[int] = None
    housenumber: Optional[str] = None
    streetname: Optional[str] = None
    apartment: Optional[str] = None
    story: Optional[float] = None

    approveddate: Optional[date] = None
    currentstatusdate: Optional[date] = None
    ordernumber: Optional[int] = None

    communityboard: Optional[int] = None
    councildistrict: Optional[int] = None

    bin: Optional[int] = Field(None, description="Building Identification Number")
    bbl: Optional[int] = Field(None, description="Borough-Block-Lot")

    # Derived temporal features
    inspection_year: Optional[int] = None
    inspection_month: Optional[int] = None
    inspection_month_name: Optional[str] = None

    days_to_status_change: Optional[int] = None
    is_rent_impairing: Optional[bool] = None

    class Config:
        orm_mode = True
        populate_by_name = True


class BuildingBase(BaseModel):
    """
    Building summary model.

    This shows aggregated stats for a building.
    Example JSON:
    {
        "buildingid": 85470,
        "full_address": "1163 Hoe Avenue, BRONX, NY 10459",
        "total_violations": 156,
        "open_violations": 12,
        "class_c_count": 8,
        "risk_score": 45.5,
        ...
    }
    """
    buildingid: int

    # Location
    boro: Optional[str] = None
    full_address: Optional[str] = None
    zip: Optional[int] = None
    nta: Optional[str] = None

    # Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Violation aggregates
    total_violations: Optional[int] = 0
    open_violations: Optional[int] = 0
    class_a_count: Optional[int] = 0
    class_b_count: Optional[int] = 0
    class_c_count: Optional[int] = 0
    class_i_count: Optional[int] = 0
    severe_violations: Optional[int] = 0

    # Dates
    first_violation_date: Optional[date] = None
    most_recent_violation_date: Optional[date] = None

    # Risk assessment
    risk_score: Optional[float] = Field(None, description="Calculated risk score")

    class Config:
        orm_mode = True


class BuildingDetail(BuildingBase):
    """
    Extended building model with additional identifiers.
    """
    bin: Optional[int] = None
    bbl: Optional[int] = None
    communityboard: Optional[int] = None
    rent_impairing_violations: Optional[int] = 0

    class Config:
        orm_mode = True


class ViolationListResponse(BaseModel):
    """
    Response model for listing violations.

    Wraps the list with metadata.
    Example:
    {
        "total": 1523,
        "page": 1,
        "page_size": 100,
        "violations": [...]
    }
    """
    total: int = Field(description="Total number of matching violations")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(description="Number of results per page")
    violations: list[ViolationBase]


class BuildingListResponse(BaseModel):
    """
    Response model for listing buildings.
    """
    total: int
    page: int = 1
    page_size: int
    buildings: list[BuildingBase]


class ErrorResponse(BaseModel):
    """
    Standard error response.

    Example:
    {
        "error": "Invalid violation class",
        "detail": "Class must be A, B, C, or I"
    }
    """
    error: str
    detail: Optional[str] = None
