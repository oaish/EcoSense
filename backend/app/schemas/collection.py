import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CollectionCreate(BaseModel):
    bin_id: uuid.UUID = Field(..., description="UUID of the bin being emptied")
    fill_level_before: Optional[Decimal] = Field(None, ge=0, le=100, description="Fill level percentage before collection")
    collected_quantity_kg: Optional[Decimal] = Field(None, gt=0, description="Waste weight collected in kg")
    fill_level_after: Optional[Decimal] = Field(None, ge=0, le=100, description="Fill level percentage after collection (e.g. 0.00)")
    notes: Optional[str] = Field(None, description="Optional collection notes or observations")


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    collection_id: int
    bin_id: uuid.UUID
    collector_id: uuid.UUID
    fill_level_before: Optional[Decimal] = None
    collected_quantity_kg: Optional[Decimal] = None
    fill_level_after: Optional[Decimal] = None
    collected_at: datetime
    notes: Optional[str] = None
