import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.config import settings
from app.schemas.waste_type import WasteTypeSummary


class ClassificationCreate(BaseModel):
    image_url: str = Field(..., min_length=1, description="Image reference, URL, or identifier for classification")
    disposal_id: Optional[int] = Field(None, gt=0, description="Optional ID of associated disposal record")


class ClassificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    classification_id: int
    user_id: uuid.UUID
    disposal_id: Optional[int] = None
    image_url: str
    predicted_waste_type: WasteTypeSummary
    confidence_score: Optional[float] = None
    model_version: Optional[str] = None
    low_confidence: bool = False
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def transform_classification(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If already a dict, ensure low_confidence is populated if not provided
            conf = data.get("confidence_score")
            if "low_confidence" not in data and conf is not None:
                data["low_confidence"] = float(conf) < settings.CLASSIFICATION_CONFIDENCE_THRESHOLD
            return data

        # ORM model instance handling
        wt_obj = getattr(data, "predicted_waste_type", None)
        wt_summary = None
        if wt_obj:
            wt_summary = WasteTypeSummary(
                waste_type_id=wt_obj.waste_type_id,
                name=wt_obj.name,
            )

        conf_score = getattr(data, "confidence_score", None)
        conf_float = float(conf_score) if conf_score is not None else None
        low_conf = bool(conf_float is not None and conf_float < settings.CLASSIFICATION_CONFIDENCE_THRESHOLD)

        return {
            "classification_id": getattr(data, "classification_id"),
            "user_id": getattr(data, "user_id"),
            "disposal_id": getattr(data, "disposal_id", None),
            "image_url": getattr(data, "image_url"),
            "predicted_waste_type": wt_summary,
            "confidence_score": conf_float,
            "model_version": getattr(data, "model_version", None),
            "low_confidence": low_conf,
            "created_at": getattr(data, "created_at"),
        }
