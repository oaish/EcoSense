import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.user import User
from app.schemas.collection import CollectionCreate


def create_collection(
    db: Session,
    collector: User,
    collection_in: CollectionCreate,
) -> CollectionRecord:
    bin_obj = db.get(Bin, collection_in.bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {collection_in.bin_id} not found",
        )

    record = CollectionRecord(
        bin_id=bin_obj.bin_id,
        collector_id=collector.user_id,
        fill_level_before=collection_in.fill_level_before,
        collected_quantity_kg=collection_in.collected_quantity_kg,
        fill_level_after=collection_in.fill_level_after,
        notes=collection_in.notes.strip() if collection_in.notes else None,
    )
    db.add(record)

    # Atomically synchronize the bin's current fill percentage if fill_level_after is provided
    if collection_in.fill_level_after is not None:
        bin_obj.current_fill_percentage = collection_in.fill_level_after

    db.commit()
    db.refresh(record)
    return record


def get_collection(db: Session, collection_id: int) -> Optional[CollectionRecord]:
    statement = (
        select(CollectionRecord)
        .options(
            joinedload(CollectionRecord.bin),
            joinedload(CollectionRecord.collector),
        )
        .where(CollectionRecord.collection_id == collection_id)
    )
    return db.scalar(statement)


def list_collections(
    db: Session,
    current_user: User,
    bin_id: Optional[uuid.UUID] = None,
    collector_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[CollectionRecord]:
    statement = (
        select(CollectionRecord)
        .options(
            joinedload(CollectionRecord.bin),
            joinedload(CollectionRecord.collector),
        )
        .order_by(CollectionRecord.collected_at.desc())
    )

    user_role = current_user.role.role_name.upper() if current_user.role else ""

    if user_role == "COLLECTOR":
        statement = statement.where(CollectionRecord.collector_id == current_user.user_id)
    elif user_role == "ADMIN" and collector_id is not None:
        statement = statement.where(CollectionRecord.collector_id == collector_id)

    if bin_id is not None:
        statement = statement.where(CollectionRecord.bin_id == bin_id)

    if start_date is not None:
        statement = statement.where(CollectionRecord.collected_at >= start_date)

    if end_date is not None:
        statement = statement.where(CollectionRecord.collected_at <= end_date)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())
