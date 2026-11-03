import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.waste_type import WasteTypeSummary


class DisposalCreate(BaseModel):
    bin_id: uuid.UUID = Field(..., description="UUID of the bin scanned during disposal")
    quantity_kg: Optional[Decimal] = Field(None, gt=0, description="Optional weight in kg")
    notes: Optional[str] = Field(None, description="Optional notes or comments")


class DisposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disposal_id: int
    bin_id: uuid.UUID
    bin_code: str
    waste_type: WasteTypeSummary
    quantity_kg: Optional[Decimal] = None
    recorded_at: datetime
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_nested_fields(cls, data: Any) -> Any:
        if hasattr(data, "bin") and data.bin:
            bin_obj = data.bin
            return {
                "disposal_id": data.disposal_id,
                "bin_id": data.bin_id,
                "bin_code": bin_obj.bin_code,
                "waste_type": WasteTypeSummary(
                    waste_type_id=bin_obj.waste_type.waste_type_id,
                    name=bin_obj.waste_type.name,
                ),
                "quantity_kg": data.quantity_kg,
                "recorded_at": data.recorded_at,
                "notes": data.notes,
            }
        return data
