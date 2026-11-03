import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.prediction.features import extract_bin_features
from ai.prediction.model import BaselineFillPredictor
from ai.prediction.predictor import BaseFillPredictor
from app.core.config import settings
from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.disposal import DisposalRecord
from app.models.fill_reading import BinFillReading
from app.models.prediction import FillPrediction

_predictor_instance: Optional[BaseFillPredictor] = None


def get_predictor() -> BaseFillPredictor:
    """Retrieve or initialize the active fill level predictor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = BaselineFillPredictor(
            model_version=settings.PREDICTION_MODEL_VERSION,
        )
    return _predictor_instance


def set_predictor(predictor: Optional[BaseFillPredictor]) -> None:
    """Override the active predictor (useful for testing and model swapping)."""
    global _predictor_instance
    _predictor_instance = predictor


def generate_bin_prediction(
    db: Session,
    bin_id: uuid.UUID,
    horizon_minutes: Optional[int] = None,
) -> FillPrediction:
    """Generate an on-demand future fill level prediction for a specific bin."""
    # 1. Verify bin exists
    bin_obj = db.query(Bin).filter(Bin.bin_id == bin_id).first()
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bin not found.",
        )

    # 2. Retrieve historical telemetry
    fill_readings = (
        db.query(BinFillReading)
        .filter(BinFillReading.bin_id == bin_id)
        .order_by(BinFillReading.recorded_at.asc())
        .all()
    )

    # 3. Enforce data sufficiency requirement
    min_readings = settings.MIN_PREDICTION_READINGS
    if len(fill_readings) < min_readings:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient historical data for prediction. A minimum of {min_readings} readings is required, but only {len(fill_readings)} were found.",
        )

    collections = (
        db.query(CollectionRecord)
        .filter(CollectionRecord.bin_id == bin_id)
        .order_by(CollectionRecord.collected_at.asc())
        .all()
    )

    disposals = (
        db.query(DisposalRecord)
        .filter(DisposalRecord.bin_id == bin_id)
        .order_by(DisposalRecord.recorded_at.asc())
        .all()
    )

    # Format tuples for feature extraction
    readings_tuples = [
        (r.recorded_at, float(r.fill_percentage)) for r in fill_readings
    ]
    collections_tuples = [
        (
            c.collected_at,
            float(c.fill_level_before) if c.fill_level_before is not None else None,
            float(c.fill_level_after) if c.fill_level_after is not None else None,
        )
        for c in collections
    ]
    disposals_tuples = [
        (
            d.recorded_at,
            float(d.quantity_kg) if d.quantity_kg is not None else None,
        )
        for d in disposals
    ]

    effective_horizon = (
        horizon_minutes
        if horizon_minutes is not None
        else settings.PREDICTION_HORIZON_MINUTES
    )
    prediction_time = datetime.now(timezone.utc)
    target_time = prediction_time + timedelta(minutes=effective_horizon)

    # 4. Extract features
    features = extract_bin_features(
        bin_id=bin_id,
        prediction_time=prediction_time,
        horizon_minutes=effective_horizon,
        readings=readings_tuples,
        collections=collections_tuples,
        disposals=disposals_tuples,
        waste_type_name=bin_obj.waste_type.name if bin_obj.waste_type else None,
        capacity_litres=(
            float(bin_obj.capacity_litres)
            if bin_obj.capacity_litres is not None
            else None
        ),
        fallback_current_fill=(
            float(bin_obj.current_fill_percentage)
            if bin_obj.current_fill_percentage is not None
            else 0.0
        ),
    )

    # 5. Invoke predictor
    predictor = get_predictor()
    result = predictor.predict(
        features=features,
        prediction_timestamp=prediction_time,
        target_timestamp=target_time,
    )

    # 6. Validate and bound prediction
    clamped_prediction = max(0.0, min(100.0, result.predicted_fill_percentage))

    prediction_record = FillPrediction(
        bin_id=bin_id,
        predicted_fill_percentage=Decimal(str(round(clamped_prediction, 2))),
        prediction_timestamp=result.prediction_timestamp,
        target_timestamp=result.target_timestamp,
        model_version=result.model_version,
        confidence_score=(
            Decimal(str(round(result.confidence_score, 4)))
            if result.confidence_score is not None
            else None
        ),
        lower_bound=(
            Decimal(str(round(result.lower_bound, 2)))
            if result.lower_bound is not None
            else None
        ),
        upper_bound=(
            Decimal(str(round(result.upper_bound, 2)))
            if result.upper_bound is not None
            else None
        ),
    )

    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)
    return prediction_record


def get_prediction(db: Session, prediction_id: int) -> FillPrediction:
    """Retrieve a single prediction by ID."""
    prediction = (
        db.query(FillPrediction)
        .filter(FillPrediction.prediction_id == prediction_id)
        .first()
    )
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction record not found.",
        )
    return prediction


def list_bin_predictions(
    db: Session,
    bin_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[FillPrediction]:
    """List historical prediction events for a specific bin."""
    bin_obj = db.query(Bin).filter(Bin.bin_id == bin_id).first()
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bin not found.",
        )

    return (
        db.query(FillPrediction)
        .filter(FillPrediction.bin_id == bin_id)
        .order_by(FillPrediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
