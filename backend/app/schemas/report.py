import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_REPORT_TYPES = {
    "OVERFLOWING",
    "DAMAGED_BIN",
    "MISSING_BIN",
    "WRONG_SEGREGATION",
    "OTHER",
}

VALID_REPORT_STATUSES = {
    "PENDING",
    "IN_PROGRESS",
    "RESOLVED",
    "REJECTED",
}


class ReportCreate(BaseModel):
    bin_id: Optional[uuid.UUID] = Field(None, description="Optional UUID of the problem bin")
    report_type: str = Field(..., description="Type of problem (OVERFLOWING, DAMAGED_BIN, MISSING_BIN, WRONG_SEGREGATION, OTHER)")
    description: Optional[str] = Field(None, description="Detailed problem description")
    image_url: Optional[str] = Field(None, description="Optional URL to uploaded issue image")

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_REPORT_TYPES:
            raise ValueError(f"Invalid report_type '{value}'. Allowed: {', '.join(sorted(VALID_REPORT_TYPES))}")
        return normalized


class ReportUpdate(BaseModel):
    status: Optional[str] = Field(None, description="New status (PENDING, IN_PROGRESS, RESOLVED, REJECTED)")
    description: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            normalized = value.strip().upper()
            if normalized not in VALID_REPORT_STATUSES:
                raise ValueError(f"Invalid status '{value}'. Allowed: {', '.join(sorted(VALID_REPORT_STATUSES))}")
            return normalized
        return value


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_id: int
    user_id: uuid.UUID
    bin_id: Optional[uuid.UUID] = None
    bin_code: Optional[str] = None
    report_type: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None

    @model_validator(mode="before")
    @classmethod
    def extract_nested_fields(cls, data: Any) -> Any:
        if hasattr(data, "report_id"):
            bin_code = data.bin.bin_code if data.bin else None
            return {
                "report_id": data.report_id,
                "user_id": data.user_id,
                "bin_id": data.bin_id,
                "bin_code": bin_code,
                "report_type": data.report_type,
                "description": data.description,
                "image_url": data.image_url,
                "status": data.status,
                "created_at": data.created_at,
                "resolved_at": data.resolved_at,
                "resolved_by": data.resolved_by,
            }
        return data
