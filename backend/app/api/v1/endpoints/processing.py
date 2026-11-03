import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.processing import ProcessingCreate, ProcessingRead
from app.services import processing_service

router = APIRouter()


@router.post(
    "/processing",
    response_model=ProcessingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Processing Record",
    description="Record a recycling or composting operation for collected waste (COLLECTOR and ADMIN only).",
)
def create_processing(
    processing_in: ProcessingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> ProcessingRead:
    record = processing_service.create_processing_record(
        db=db,
        processor=current_user,
        processing_in=processing_in,
    )
    return ProcessingRead.model_validate(record)


@router.get(
    "/processing",
    response_model=List[ProcessingRead],
    summary="List Processing Records",
    description="Retrieve processing records with optional filters (STAFF, COLLECTOR, and ADMIN only).",
)
def list_processing(
    processing_type: Optional[str] = Query(None, description="Filter by processing type (RECYCLING, COMPOSTING)"),
    status: Optional[str] = Query(None, description="Filter by status (COMPLETED, PARTIALLY_PROCESSED, REJECTED)"),
    collection_id: Optional[int] = Query(None, description="Filter by source collection ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STAFF", "COLLECTOR", "ADMIN")),
) -> List[ProcessingRead]:
    records = processing_service.list_processing_records(
        db=db,
        current_user=current_user,
        processing_type=processing_type,
        status_filter=status,
        collection_id=collection_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [ProcessingRead.model_validate(r) for r in records]


@router.get(
    "/processing/{processing_id}",
    response_model=ProcessingRead,
    summary="Get Processing Record by ID",
    description="Retrieve details of a specific processing record (STAFF, COLLECTOR, and ADMIN only).",
)
def get_processing(
    processing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STAFF", "COLLECTOR", "ADMIN")),
) -> ProcessingRead:
    record = processing_service.get_processing_record(db=db, processing_id=processing_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing record with ID {processing_id} not found",
        )
    return ProcessingRead.model_validate(record)


@router.get(
    "/collections/{collection_id}/processing",
    response_model=List[ProcessingRead],
    summary="Get Processing Records for a Collection",
    description="Retrieve all recycling and composting processing records linked to a specific collection (STAFF, COLLECTOR, and ADMIN only).",
)
def get_collection_processing(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STAFF", "COLLECTOR", "ADMIN")),
) -> List[ProcessingRead]:
    records = processing_service.list_collection_processing_records(
        db=db,
        collection_id=collection_id,
    )
    return [ProcessingRead.model_validate(r) for r in records]


@router.get(
    "/bins/{bin_id}/processing",
    response_model=List[ProcessingRead],
    summary="Get Processing History for a Bin",
    description="Retrieve processing history for a specific bin via relational joins through collection records (STAFF, COLLECTOR, and ADMIN only).",
)
def get_bin_processing(
    bin_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STAFF", "COLLECTOR", "ADMIN")),
) -> List[ProcessingRead]:
    records = processing_service.list_bin_processing_records(
        db=db,
        bin_id=bin_id,
        skip=skip,
        limit=limit,
    )
    return [ProcessingRead.model_validate(r) for r in records]
