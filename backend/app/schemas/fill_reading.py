import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_FILL_SOURCES = {"MANUAL", "IOT", "ESTIMATED"}


class FillReadingCreate(BaseModel):
    fill_percentage: Decimal = Field(..., ge=0, le=100, description="Fill percentage measurement (0 to 100)")
    source: str = Field("MANUAL", description="Measurement source (MANUAL, IOT, ESTIMATED)")
    notes: Optional[str] = Field(None, description="Optional measurement notes")

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_FILL_SOURCES:
            raise ValueError(f"Invalid source '{value}'. Allowed: {', '.join(sorted(VALID_FILL_SOURCES))}")
        return normalized


class FillReadingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reading_id: int
    bin_id: uuid.UUID
    fill_percentage: Decimal
    source: str
    recorded_at: datetime
    notes: Optional[str] = None
