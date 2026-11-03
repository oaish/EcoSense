import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.models.disposal import DisposalRecord
from app.models.user import User
from app.schemas.disposal import DisposalCreate


def create_disposal(
    db: Session,
    user: User,
    disposal_in: DisposalCreate,
) -> DisposalRecord:
    # 1. Fetch bin with relationships
    statement = (
        select(Bin)
        .options(joinedload(Bin.waste_type), joinedload(Bin.location))
        .where(Bin.bin_id == disposal_in.bin_id)
    )
    bin_obj = db.scalar(statement)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {disposal_in.bin_id} not found",
        )

    # 2. Status validation
    if bin_obj.status == "FULL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bin is currently full.",
        )

    if bin_obj.status in {"DAMAGED", "MISSING", "INACTIVE"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bin is currently {bin_obj.status.lower()} and unavailable for disposal.",
        )

    # 3. Create disposal record
    record = DisposalRecord(
        user_id=user.user_id,
        bin_id=bin_obj.bin_id,
        quantity_kg=disposal_in.quantity_kg,
        notes=disposal_in.notes.strip() if disposal_in.notes else None,
    )
    db.add(record)
    db.flush()

    # 4. Atomically award points in the immutable ledger
    from app.services.gamification_service import award_points_for_disposal

    award_points_for_disposal(db, user, record)

    db.commit()
    db.refresh(record)
    return record


def get_disposal(db: Session, disposal_id: int) -> Optional[DisposalRecord]:
    statement = (
        select(DisposalRecord)
        .options(
            joinedload(DisposalRecord.bin).joinedload(Bin.waste_type),
            joinedload(DisposalRecord.bin).joinedload(Bin.location),
            joinedload(DisposalRecord.user),
        )
        .where(DisposalRecord.disposal_id == disposal_id)
    )
    return db.scalar(statement)


def list_disposals(
    db: Session,
    current_user: User,
    user_id: Optional[uuid.UUID] = None,
    bin_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[DisposalRecord]:
    statement = (
        select(DisposalRecord)
        .options(
            joinedload(DisposalRecord.bin).joinedload(Bin.waste_type),
            joinedload(DisposalRecord.bin).joinedload(Bin.location),
        )
        .order_by(DisposalRecord.recorded_at.desc())
    )

    user_role = current_user.role.role_name.upper() if current_user.role else ""

    # Students and Staff only see their own disposal history
    if user_role in {"STUDENT", "STAFF"}:
        statement = statement.where(DisposalRecord.user_id == current_user.user_id)
    elif user_role == "ADMIN" and user_id is not None:
        statement = statement.where(DisposalRecord.user_id == user_id)

    if bin_id is not None:
        statement = statement.where(DisposalRecord.bin_id == bin_id)

    if start_date is not None:
        statement = statement.where(DisposalRecord.recorded_at >= start_date)

    if end_date is not None:
        statement = statement.where(DisposalRecord.recorded_at <= end_date)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())
