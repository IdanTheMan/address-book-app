from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class AddressCreate(BaseModel):
    street: str = Field(..., min_length=1, max_length=255, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: Optional[str] = Field(None, max_length=100, description="State or province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal / ZIP code")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees (WGS-84)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees (WGS-84)")


class AddressResponse(BaseModel):
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