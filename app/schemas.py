"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

class AddressCreate(BaseModel):
    """Partial update — only include the fields you want to change."""

    street: str = Field(..., min_length=1, max_length=255, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal / ZIP code")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees (WGS-84)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees (WGS-84)")


class AddressUpdate(BaseModel):
    """Partial update — only include the fields you want to change."""

    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AddressUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self

class AddressResponse(BaseModel):
    """Full address representation returned by the API."""

    id: int
    street: str
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)