import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.processing import ProcessingRecord
from app.models.user import User
from app.schemas.processing import ProcessingCreate

# Compatibility rules between Waste Types and Processing Types
COMPOSTING_TYPES = {"WET_ORGANIC", "GARDEN", "FOOD_WASTE", "ORGANIC", "WET", "COMPOSTABLE"}
RECYCLING_TYPES = {
    "DRY_RECYCLABLE",
    "PAPER",
    "METAL",
    "E_WASTE",
    "E-WASTE",
    "PLASTIC",
    "GLASS",
    "CARDBOARD",
}


def is_compatible_processing(waste_type_name: str, processing_type: str) -> bool:
    wt = waste_type_name.strip().upper()
    pt = processing_type.strip().upper()

    if pt == "COMPOSTING":
        if wt in COMPOSTING_TYPES or any(
            k in wt for k in ["WET", "ORGANIC", "GARDEN", "FOOD", "COMPOST", "HORTICULTURE", "LEAF", "BIO"]
        ):
            return True
        return False
    elif pt == "RECYCLING":
        if wt in RECYCLING_TYPES or any(
            k in wt for k in ["DRY", "RECYCL", "PAPER", "METAL", "E_WASTE", "E-WASTE", "PLASTIC", "GLASS", "CARD", "TIN", "CAN"]
        ):
            return True
        return False
    return False


def create_processing_record(
    db: Session,
    processor: User,
    processing_in: ProcessingCreate,
) -> ProcessingRecord:
    # 1. Validate collection exists
    collection = db.scalar(
        select(CollectionRecord)
        .options(
            joinedload(CollectionRecord.bin).joinedload(Bin.waste_type),
        )
        .where(CollectionRecord.collection_id == processing_in.collection_id)
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection record with ID {processing_in.collection_id} not found",
        )

    # 2. Determine waste type from collection -> bin -> waste_type
    bin_obj = collection.bin
    waste_type = bin_obj.waste_type if bin_obj else None
    waste_type_name = waste_type.name.upper() if waste_type else "UNKNOWN"

    # 3. Validate processing_type compatibility with waste type
    if not is_compatible_processing(waste_type_name, processing_in.processing_type):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Processing type '{processing_in.processing_type}' is incompatible with waste type '{waste_type_name}'",
        )

    # 4. Validate quantity against collection if collected_quantity_kg is known
    requested_qty = Decimal(str(processing_in.quantity_kg))
    if requested_qty <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Processing quantity must be greater than zero",
        )

    if collection.collected_quantity_kg is not None:
        existing_processed = db.scalar(
            select(func.coalesce(func.sum(ProcessingRecord.quantity_kg), Decimal("0.0")))
            .where(
                ProcessingRecord.collection_id == collection.collection_id,
                ProcessingRecord.status != "REJECTED",
            )
        )
        cumulative_qty = (existing_processed or Decimal("0.0")) + requested_qty
        if cumulative_qty > collection.collected_quantity_kg:
            remaining_qty = collection.collected_quantity_kg - (existing_processed or Decimal("0.0"))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Requested processing quantity ({requested_qty} kg) exceeds remaining collected quantity "
                    f"({max(Decimal('0.0'), remaining_qty)} kg). Total collected: {collection.collected_quantity_kg} kg, "
                    f"Already processed: {existing_processed or Decimal('0.0')} kg."
                ),
            )

    # 5. Build and persist processing record
    processed_at = processing_in.processed_at or datetime.now(timezone.utc)
    record = ProcessingRecord(
        collection_id=collection.collection_id,
        processing_type=processing_in.processing_type,
        quantity_kg=requested_qty,
        processed_at=processed_at,
        processed_by=processor.user_id,
        status=processing_in.status or "COMPLETED",
        notes=processing_in.notes.strip() if processing_in.notes else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_processing_record(db: Session, processing_id: int) -> Optional[ProcessingRecord]:
    statement = (
        select(ProcessingRecord)
        .options(
            joinedload(ProcessingRecord.collection),
            joinedload(ProcessingRecord.processor),
        )
        .where(ProcessingRecord.processing_id == processing_id)
    )
    return db.scalar(statement)


def list_processing_records(
    db: Session,
    current_user: User,
    processing_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    collection_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[ProcessingRecord]:
    statement = (
        select(ProcessingRecord)
        .options(
            joinedload(ProcessingRecord.collection),
            joinedload(ProcessingRecord.processor),
        )
        .order_by(ProcessingRecord.processed_at.desc())
    )

    if processing_type:
        statement = statement.where(ProcessingRecord.processing_type == processing_type.strip().upper())

    if status_filter:
        statement = statement.where(ProcessingRecord.status == status_filter.strip().upper())

    if collection_id is not None:
        statement = statement.where(ProcessingRecord.collection_id == collection_id)

    if start_date is not None:
        statement = statement.where(ProcessingRecord.processed_at >= start_date)

    if end_date is not None:
        statement = statement.where(ProcessingRecord.processed_at <= end_date)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def list_collection_processing_records(
    db: Session,
    collection_id: int,
) -> List[ProcessingRecord]:
    # Check if collection exists
    collection = db.get(CollectionRecord, collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection record with ID {collection_id} not found",
        )

    statement = (
        select(ProcessingRecord)
        .options(
            joinedload(ProcessingRecord.collection),
            joinedload(ProcessingRecord.processor),
        )
        .where(ProcessingRecord.collection_id == collection_id)
        .order_by(ProcessingRecord.processed_at.desc())
    )
    return list(db.scalars(statement).all())


def list_bin_processing_records(
    db: Session,
    bin_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[ProcessingRecord]:
    bin_obj = db.get(Bin, bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {bin_id} not found",
        )

    statement = (
        select(ProcessingRecord)
        .join(CollectionRecord, ProcessingRecord.collection_id == CollectionRecord.collection_id)
        .options(
            joinedload(ProcessingRecord.collection),
            joinedload(ProcessingRecord.processor),
        )
        .where(CollectionRecord.bin_id == bin_id)
        .order_by(ProcessingRecord.processed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())
