import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionRequest(BaseModel):
    """Optional parameters when triggering on-demand bin fill prediction."""

    horizon_minutes: Optional[int] = Field(
        None,
        gt=0,
        le=1440,
        description="Forecast horizon ahead in minutes (default configured via PREDICTION_HORIZON_MINUTES)",
    )


class PredictionRead(BaseModel):
    """Serialization schema for a persisted bin fill prediction event."""

    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    bin_id: uuid.UUID
    predicted_fill_percentage: float
    prediction_timestamp: datetime
    target_timestamp: datetime
    model_version: str
    confidence_score: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def convert_decimals(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data

        return {
            "prediction_id": getattr(data, "prediction_id"),
            "bin_id": getattr(data, "bin_id"),
            "predicted_fill_percentage": float(getattr(data, "predicted_fill_percentage")),
            "prediction_timestamp": getattr(data, "prediction_timestamp"),
            "target_timestamp": getattr(data, "target_timestamp"),
            "model_version": getattr(data, "model_version"),
            "confidence_score": (
                float(getattr(data, "confidence_score"))
                if getattr(data, "confidence_score", None) is not None
                else None
            ),
            "lower_bound": (
                float(getattr(data, "lower_bound"))
                if getattr(data, "lower_bound", None) is not None
                else None
            ),
            "upper_bound": (
                float(getattr(data, "upper_bound"))
                if getattr(data, "upper_bound", None) is not None
                else None
            ),
            "created_at": getattr(data, "created_at"),
        }
