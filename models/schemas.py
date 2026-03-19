"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────────────
#  Shared coordinate validators
# ──────────────────────────────────────────────

def _validate_latitude(v: float) -> float:
    if not (-90 <= v <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    return v


def _validate_longitude(v: float) -> float:
    if not (-180 <= v <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")
    return v


# ──────────────────────────────────────────────
#  Create schema (all required fields)
# ──────────────────────────────────────────────

class AddressCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Home"],
        description="A human-readable label for this address.",
    )
    street: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["123 Main Street"],
        description="Street address line.",
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Surat"],
        description="City or locality.",
    )
    state: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["Gujarat"],
        description="State, province, or region (optional).",
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["India"],
        description="Country name.",
    )
    postal_code: Optional[str] = Field(
        default=None,
        max_length=20,
        examples=["395004"],
        description="ZIP or postal code (optional).",
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        examples=[21.230639],
        description="Latitude in decimal degrees (-90 to 90).",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        examples=[72.821389],
        description="Longitude in decimal degrees (-180 to 180).",
    )

    @field_validator("name", "street", "city", "country")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field must not be blank or whitespace only.")
        return v

    @field_validator("state", "postal_code", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Home",
                    "street": "123 Main Street",
                    "city": "Surat",
                    "state": "Gujarat",
                    "country": "India",
                    "postal_code": "395004",
                    "latitude": 21.230639,
                    "longitude": 72.821389,
                }
            ]
        }
    }


# ──────────────────────────────────────────────
#  Update schema (all fields optional)
# ──────────────────────────────────────────────

class AddressUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    street: Optional[str] = Field(default=None, min_length=1, max_length=255)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    @field_validator("name", "street", "city", "country", mode="before")
    @classmethod
    def strip_and_check(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Field must not be blank or whitespace only.")
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("At least one field must be provided for update.")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Surat",
                    "latitude": 21.234833,
                    "longitude": 72.820778,
                }
            ]
        }
    }


# ──────────────────────────────────────────────
#  Response schema
# ──────────────────────────────────────────────

class AddressResponse(BaseModel):
    id:          int
    name:        str
    street:      str
    city:        str
    state:       Optional[str]
    country:     str
    postal_code: Optional[str]
    latitude:    float
    longitude:   float
    created_at:  Optional[datetime]
    updated_at:  Optional[datetime]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
#  Nearby search response (includes distance)
# ──────────────────────────────────────────────

class AddressWithDistance(AddressResponse):
    distance_km: float = Field(..., description="Distance from the query point in kilometers.")
