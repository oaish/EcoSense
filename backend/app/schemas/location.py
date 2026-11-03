from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    name: str = Field(..., max_length=150, description="Name of the campus location (e.g. Canteen, Computer Lab)")
    location_type: str = Field(..., max_length=50, description="Type or category of location")
    building: Optional[str] = Field(None, max_length=100, description="Building name")
    floor: Optional[str] = Field(None, max_length=30, description="Floor level/number")
    latitude: Optional[Decimal] = Field(None, description="GPS Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, description="GPS Longitude coordinate")
    description: Optional[str] = Field(None, description="Detailed description or notes")


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    location_type: Optional[str] = Field(None, max_length=50)
    building: Optional[str] = Field(None, max_length=100)
    floor: Optional[str] = Field(None, max_length=30)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LocationRead(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    location_id: int
    is_active: bool
    created_at: datetime


class LocationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: int
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None
