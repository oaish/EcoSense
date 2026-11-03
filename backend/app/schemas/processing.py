import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessingCreate(BaseModel):
    collection_id: int = Field(..., description="ID of the source collection record")
    processing_type: str = Field(
        ...,
        description="Type of processing operation: RECYCLING or COMPOSTING",
    )
    quantity_kg: Decimal = Field(
        ...,
        gt=0,
        description="Quantity of collected waste processed in kg (must be > 0)",
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Optional processing timestamp (defaults to current time)",
    )
    status: Optional[str] = Field(
        "COMPLETED",
        description="Processing status: COMPLETED, PARTIALLY_PROCESSED, or REJECTED",
    )
    notes: Optional[str] = Field(
        None,
        description="Optional notes or details regarding the processing batch",
    )

    @field_validator("processing_type")
    @classmethod
    def validate_processing_type(cls, v: str) -> str:
        normalized = v.strip().upper()
        if normalized not in {"RECYCLING", "COMPOSTING"}:
            raise ValueError("processing_type must be either 'RECYCLING' or 'COMPOSTING'")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> str:
        if v is None:
            return "COMPLETED"
        normalized = v.strip().upper()
        if normalized not in {"COMPLETED", "PARTIALLY_PROCESSED", "REJECTED"}:
            raise ValueError("status must be 'COMPLETED', 'PARTIALLY_PROCESSED', or 'REJECTED'")
        return normalized


class ProcessingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    processing_id: int
    collection_id: int
    processing_type: str
    quantity_kg: Decimal
    processed_at: datetime
    processed_by: uuid.UUID
    status: str
    notes: Optional[str] = None
    created_at: datetime
