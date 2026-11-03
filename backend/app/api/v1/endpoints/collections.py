import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.collection import CollectionCreate, CollectionRead
from app.services import collection_service

router = APIRouter()


@router.post(
    "",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record Waste Collection",
    description="Record a completed waste collection event from a bin, recording before/after fill snapshots and collected weight (COLLECTOR and ADMIN only).",
)
def record_collection(
    collection_in: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> CollectionRead:
    record = collection_service.create_collection(
        db=db,
        collector=current_user,
        collection_in=collection_in,
    )
    return CollectionRead.model_validate(record)


@router.get(
    "",
    response_model=List[CollectionRead],
    summary="List Waste Collections",
    description="Retrieve waste collection logs with optional filters (COLLECTOR views their own operations; ADMIN views all).",
)
def list_collections(
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by bin ID"),
    collector_id: Optional[uuid.UUID] = Query(None, description="Filter by collector user ID (ADMIN only)"),
    start_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> List[CollectionRead]:
    records = collection_service.list_collections(
        db=db,
        current_user=current_user,
        bin_id=bin_id,
        collector_id=collector_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [CollectionRead.model_validate(r) for r in records]


@router.get(
    "/{collection_id}",
    response_model=CollectionRead,
    summary="Get Collection Record by ID",
    description="Retrieve details of a specific collection event.",
)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> CollectionRead:
    record = collection_service.get_collection(db=db, collection_id=collection_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection record with ID {collection_id} not found",
        )

    user_role = current_user.role.role_name.upper() if current_user.role else ""
    if user_role == "COLLECTOR" and record.collector_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted",
        )

    return CollectionRead.model_validate(record)
