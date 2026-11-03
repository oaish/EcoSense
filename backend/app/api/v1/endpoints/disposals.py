import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.disposal import DisposalCreate, DisposalRead
from app.services import disposal_service

router = APIRouter()


@router.post(
    "",
    response_model=DisposalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record Waste Disposal",
    description="Record a waste disposal event into a scanned physical bin (STUDENT and STAFF only).",
)
def record_disposal(
    disposal_in: DisposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT", "STAFF")),
) -> DisposalRead:
    record = disposal_service.create_disposal(
        db=db,
        user=current_user,
        disposal_in=disposal_in,
    )
    return DisposalRead.model_validate(record)


@router.get(
    "",
    response_model=List[DisposalRead],
    summary="List Disposal Records",
    description="Retrieve waste disposal records. Students and Staff view their personal history; Admins can view platform history.",
)
def list_disposals(
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by bin ID"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID (Admin only)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter by end timestamp"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[DisposalRead]:
    records = disposal_service.list_disposals(
        db=db,
        current_user=current_user,
        user_id=user_id,
        bin_id=bin_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [DisposalRead.model_validate(r) for r in records]


@router.get(
    "/{disposal_id}",
    response_model=DisposalRead,
    summary="Get Disposal Record by ID",
    description="Retrieve details of a specific disposal event.",
)
def get_disposal(
    disposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DisposalRead:
    record = disposal_service.get_disposal(db=db, disposal_id=disposal_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disposal record with ID {disposal_id} not found",
        )

    user_role = current_user.role.role_name.upper() if current_user.role else ""
    if user_role in {"STUDENT", "STAFF"} and record.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted",
        )

    return DisposalRead.model_validate(record)
