import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.prediction import PredictionRead, PredictionRequest
from app.services.prediction_service import (
    generate_bin_prediction,
    get_prediction,
    list_bin_predictions,
)

router = APIRouter()


@router.post(
    "/bins/{bin_id}/predictions",
    response_model=PredictionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Bin Fill Prediction",
    description="Generates an on-demand future fill level prediction for a physical bin using historical accumulation telemetry.",
)
def create_bin_prediction_endpoint(
    bin_id: uuid.UUID,
    payload: Optional[PredictionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> PredictionRead:
    horizon = payload.horizon_minutes if payload else None
    prediction = generate_bin_prediction(
        db=db,
        bin_id=bin_id,
        horizon_minutes=horizon,
    )
    return PredictionRead.model_validate(prediction)


@router.get(
    "/bins/{bin_id}/predictions",
    response_model=List[PredictionRead],
    summary="List Predictions for Bin",
    description="Lists historical prediction events for a specific bin, ordered by creation date descending.",
)
def list_bin_predictions_endpoint(
    bin_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of predictions to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of predictions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[PredictionRead]:
    predictions = list_bin_predictions(
        db=db,
        bin_id=bin_id,
        skip=skip,
        limit=limit,
    )
    return [PredictionRead.model_validate(p) for p in predictions]


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionRead,
    summary="Get Prediction by ID",
    description="Retrieves a specific prediction record by its ID.",
)
def get_prediction_endpoint(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PredictionRead:
    prediction = get_prediction(db=db, prediction_id=prediction_id)
    return PredictionRead.model_validate(prediction)
