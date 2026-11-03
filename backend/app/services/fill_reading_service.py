import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bin import Bin
from app.models.fill_reading import BinFillReading
from app.schemas.fill_reading import FillReadingCreate


def create_fill_reading(
    db: Session,
    bin_id: uuid.UUID,
    reading_in: FillReadingCreate,
) -> BinFillReading:
    bin_obj = db.get(Bin, bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {bin_id} not found",
        )

    reading = BinFillReading(
        bin_id=bin_obj.bin_id,
        fill_percentage=reading_in.fill_percentage,
        source=reading_in.source,
        notes=reading_in.notes.strip() if reading_in.notes else None,
    )
    db.add(reading)

    # Atomically synchronize the bin's current state with the latest reading
    bin_obj.current_fill_percentage = reading_in.fill_percentage

    db.commit()
    db.refresh(reading)
    return reading


def get_fill_reading(db: Session, reading_id: int) -> Optional[BinFillReading]:
    return db.get(BinFillReading, reading_id)


def list_fill_readings_for_bin(
    db: Session,
    bin_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[BinFillReading]:
    bin_obj = db.get(Bin, bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {bin_id} not found",
        )

    statement = (
        select(BinFillReading)
        .where(BinFillReading.bin_id == bin_id)
        .order_by(BinFillReading.recorded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())
