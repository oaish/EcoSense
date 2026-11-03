import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.fill_reading import FillReadingCreate, FillReadingRead
from app.services import fill_reading_service

router = APIRouter()


@router.post(
    "/bins/{bin_id}/fill-readings",
    response_model=FillReadingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record Bin Fill Reading",
    description="Record a manual/sensor fill level reading for a bin and synchronize its current fill state (COLLECTOR and ADMIN only).",
)
def record_bin_fill_reading(
    bin_id: uuid.UUID,
    reading_in: FillReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> FillReadingRead:
    reading = fill_reading_service.create_fill_reading(
        db=db,
        bin_id=bin_id,
        reading_in=reading_in,
    )
    return FillReadingRead.model_validate(reading)


@router.get(
    "/bins/{bin_id}/fill-readings",
    response_model=List[FillReadingRead],
    summary="List Historical Fill Readings for a Bin",
    description="Retrieve chronological historical fill readings for a specific bin.",
)
def list_bin_fill_readings(
    bin_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[FillReadingRead]:
    readings = fill_reading_service.list_fill_readings_for_bin(
        db=db,
        bin_id=bin_id,
        skip=skip,
        limit=limit,
    )
    return [FillReadingRead.model_validate(r) for r in readings]


@router.get(
    "/fill-readings/{reading_id}",
    response_model=FillReadingRead,
    summary="Get Fill Reading by ID",
    description="Retrieve details of an individual historical fill level reading.",
)
def get_fill_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FillReadingRead:
    reading = fill_reading_service.get_fill_reading(db=db, reading_id=reading_id)
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fill reading with ID {reading_id} not found",
        )
    return FillReadingRead.model_validate(reading)
