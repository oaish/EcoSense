from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WasteTypeBase(BaseModel):
    name: str = Field(..., max_length=50, description="Unique waste category name (e.g. WET_ORGANIC, DRY_RECYCLABLE)")
    description: Optional[str] = Field(None, description="Waste type description and examples")


class WasteTypeCreate(WasteTypeBase):
    pass


class WasteTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WasteTypeRead(WasteTypeBase):
    model_config = ConfigDict(from_attributes=True)

    waste_type_id: int
    is_active: bool


class WasteTypeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    waste_type_id: int
    name: str
