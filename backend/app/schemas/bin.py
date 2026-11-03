import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.location import LocationSummary
from app.schemas.waste_type import WasteTypeSummary

VALID_BIN_STATUSES = {"ACTIVE", "FULL", "DAMAGED", "MISSING", "INACTIVE"}


class BinBase(BaseModel):
    bin_code: str = Field(..., max_length=50, description="Unique physical bin identifier (e.g. B-001)")
    location_id: int = Field(..., description="Foreign key to the physical campus location")
    waste_type_id: int = Field(..., description="Foreign key to the designated waste type category")
    capacity_litres: Optional[Decimal] = Field(None, ge=0, description="Total volume capacity in litres")
    installed_at: Optional[datetime] = Field(None, description="Timestamp when the bin was deployed on campus")


class BinCreate(BinBase):
    pass


class BinUpdate(BaseModel):
    location_id: Optional[int] = None
    waste_type_id: Optional[int] = None
    capacity_litres: Optional[Decimal] = Field(None, ge=0)
    current_fill_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    installed_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            normalized = value.strip().upper()
            if normalized not in VALID_BIN_STATUSES:
                raise ValueError(f"Invalid status '{value}'. Allowed: {', '.join(sorted(VALID_BIN_STATUSES))}")
            return normalized
        return value


class BinRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bin_id: uuid.UUID
    bin_code: str
    location: LocationSummary
    waste_type: WasteTypeSummary
    capacity_litres: Optional[Decimal] = None
    qr_token: uuid.UUID
    current_fill_percentage: Optional[Decimal] = None
    status: str
    installed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BinQRRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bin_id: uuid.UUID
    bin_code: str
    location: Optional[LocationSummary] = None
    waste_type: Optional[WasteTypeSummary] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    waste_type_id: Optional[int] = None
    waste_type_name: Optional[str] = None
    waste_type_code: Optional[str] = None
    color_code: Optional[str] = None
    capacity_litres: Optional[Decimal] = None
    capacity_liters: Optional[Decimal] = None
    current_fill_percentage: Optional[Decimal] = None
    status: str

    @model_validator(mode="before")
    @classmethod
    def populate_flat_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            loc = data.get("location")
            if isinstance(loc, dict):
                data.setdefault("location_id", loc.get("location_id"))
                data.setdefault("location_name", loc.get("name"))
                data.setdefault("building", loc.get("building"))
                data.setdefault("floor", loc.get("floor"))
            wt = data.get("waste_type")
            if isinstance(wt, dict):
                data.setdefault("waste_type_id", wt.get("waste_type_id"))
                data.setdefault("waste_type_name", wt.get("name"))
                data.setdefault("waste_type_code", wt.get("name"))
            if "capacity_litres" in data and "capacity_liters" not in data:
                data["capacity_liters"] = data["capacity_litres"]
            return data

        # ORM model instance
        loc = getattr(data, "location", None)
        wt = getattr(data, "waste_type", None)
        cap = getattr(data, "capacity_litres", None)

        wt_name = getattr(wt, "name", "") if wt else ""
        color = "#10B981"
        upper_wt = wt_name.upper()
        if "DRY" in upper_wt or "RECYCL" in upper_wt or "PLASTIC" in upper_wt or "PAPER" in upper_wt:
            color = "#0284C7"
        elif "WET" in upper_wt or "ORGANIC" in upper_wt or "COMPOST" in upper_wt:
            color = "#10B981"
        elif "E-WASTE" in upper_wt or "ELECTR" in upper_wt:
            color = "#8B5CF6"
        elif "HAZARD" in upper_wt:
            color = "#EF4444"

        loc_summary = None
        if loc:
            loc_summary = LocationSummary(
                location_id=loc.location_id,
                name=loc.name,
                building=loc.building,
                floor=loc.floor,
            )

        wt_summary = None
        if wt:
            wt_summary = WasteTypeSummary(
                waste_type_id=wt.waste_type_id,
                name=wt.name,
            )

        return {
            "bin_id": getattr(data, "bin_id"),
            "bin_code": getattr(data, "bin_code"),
            "location": loc_summary,
            "waste_type": wt_summary,
            "location_id": getattr(loc, "location_id", None) if loc else None,
            "location_name": getattr(loc, "name", "Campus Location") if loc else "Campus Location",
            "building": getattr(loc, "building", None) if loc else None,
            "floor": getattr(loc, "floor", None) if loc else None,
            "waste_type_id": getattr(wt, "waste_type_id", None) if wt else None,
            "waste_type_name": getattr(wt, "name", "General Waste") if wt else "General Waste",
            "waste_type_code": getattr(wt, "name", "GENERAL") if wt else "GENERAL",
            "color_code": color,
            "capacity_litres": cap,
            "capacity_liters": cap,
            "current_fill_percentage": getattr(data, "current_fill_percentage", Decimal("0.0")),
            "status": getattr(data, "status", "ACTIVE"),
        }
