import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.bin import BinCreate, BinQRRead, BinRead, BinUpdate
from app.services import bin_service, location_service, waste_type_service

router = APIRouter()


@router.post(
    "",
    response_model=BinRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Bin",
    description="Deploy a new physical waste bin and assign its location & waste type (ADMIN only).",
)
def create_bin(
    bin_in: BinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> BinRead:
    # 1. Check if bin_code already exists
    existing = bin_service.get_bin_by_code(db=db, bin_code=bin_in.bin_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bin with code '{bin_in.bin_code.strip().upper()}' already exists",
        )

    # 2. Check location exists
    location = location_service.get_location(db=db, location_id=bin_in.location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {bin_in.location_id} not found",
        )

    # 3. Check waste type exists
    waste_type = waste_type_service.get_waste_type(db=db, waste_type_id=bin_in.waste_type_id)
    if not waste_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waste type with ID {bin_in.waste_type_id} not found",
        )

    new_bin = bin_service.create_bin(db=db, bin_in=bin_in)
    return BinRead.model_validate(new_bin)


@router.get(
    "",
    response_model=List[BinRead],
    summary="List Bins",
    description="List campus bins with filtering by location, waste type, and status.",
)
def list_bins(
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    waste_type_id: Optional[int] = Query(None, description="Filter by waste type ID"),
    status: Optional[str] = Query(None, description="Filter by bin status (e.g. ACTIVE, FULL, DAMAGED)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[BinRead]:
    bins = bin_service.list_bins(
        db=db,
        skip=skip,
        limit=limit,
        location_id=location_id,
        waste_type_id=waste_type_id,
        status=status,
    )
    return [BinRead.model_validate(b) for b in bins]


@router.get(
    "/public/{qr_token}",
    response_model=BinQRRead,
    summary="Public Lookup Bin by QR Token",
    description="Retrieve public-safe bin details when scanning a physical QR code (No authentication required).",
)
def public_lookup_bin_by_qr(
    qr_token: uuid.UUID,
    db: Session = Depends(get_db),
) -> BinQRRead:
    bin_obj = bin_service.get_bin_by_qr_token(db=db, qr_token=qr_token)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bin not found for the provided QR token",
        )
    return BinQRRead.model_validate(bin_obj)


@router.get(
    "/qr/{qr_token}",
    response_model=BinQRRead,
    summary="Lookup Bin by QR Token",
    description="Retrieve essential bin details when scanning a physical QR code (All authenticated roles).",
)
def lookup_bin_by_qr(
    qr_token: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BinQRRead:
    bin_obj = bin_service.get_bin_by_qr_token(db=db, qr_token=qr_token)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bin not found for the provided QR token",
        )
    return BinQRRead.model_validate(bin_obj)


@router.get(
    "/{bin_id}",
    response_model=BinRead,
    summary="Get Bin by ID",
    description="Retrieve detailed specifications and status for a specific bin.",
)
def get_bin(
    bin_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BinRead:
    bin_obj = bin_service.get_bin_by_id(db=db, bin_id=bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {bin_id} not found",
        )
    return BinRead.model_validate(bin_obj)


@router.patch(
    "/{bin_id}",
    response_model=BinRead,
    summary="Update Bin",
    description="Update bin parameters, location, designated waste type, fill level, or operational status (ADMIN only).",
)
def update_bin(
    bin_id: uuid.UUID,
    bin_in: BinUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> BinRead:
    bin_obj = bin_service.get_bin_by_id(db=db, bin_id=bin_id)
    if not bin_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bin with ID {bin_id} not found",
        )

    if bin_in.location_id is not None:
        location = location_service.get_location(db=db, location_id=bin_in.location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {bin_in.location_id} not found",
            )

    if bin_in.waste_type_id is not None:
        waste_type = waste_type_service.get_waste_type(db=db, waste_type_id=bin_in.waste_type_id)
        if not waste_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waste type with ID {bin_in.waste_type_id} not found",
            )

    updated = bin_service.update_bin(
        db=db,
        bin_obj=bin_obj,
        bin_in=bin_in,
    )
    return BinRead.model_validate(updated)
