from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.waste_type import (
    WasteTypeCreate,
    WasteTypeRead,
    WasteTypeUpdate,
)
from app.services import waste_type_service

router = APIRouter()


@router.get(
    "",
    response_model=List[WasteTypeRead],
    summary="List Waste Types",
    description="Retrieve all active waste category types.",
)
def list_waste_types(
    is_active_only: bool = Query(True, description="Filter for active waste types only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[WasteTypeRead]:
    waste_types = waste_type_service.list_waste_types(db=db, is_active_only=is_active_only)
    return [WasteTypeRead.model_validate(wt) for wt in waste_types]


@router.post(
    "",
    response_model=WasteTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Waste Type",
    description="Register a new waste classification category (ADMIN only).",
)
def create_waste_type(
    waste_type_in: WasteTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> WasteTypeRead:
    existing = waste_type_service.get_waste_type_by_name(db=db, name=waste_type_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Waste type '{waste_type_in.name.strip().upper()}' already exists",
        )
    waste_type = waste_type_service.create_waste_type(db=db, waste_type_in=waste_type_in)
    return WasteTypeRead.model_validate(waste_type)


@router.patch(
    "/{waste_type_id}",
    response_model=WasteTypeRead,
    summary="Update Waste Type",
    description="Update waste type details or active status (ADMIN only).",
)
def update_waste_type(
    waste_type_id: int,
    waste_type_in: WasteTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> WasteTypeRead:
    waste_type = waste_type_service.get_waste_type(db=db, waste_type_id=waste_type_id)
    if not waste_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waste type with ID {waste_type_id} not found",
        )
    if waste_type_in.name is not None:
        name_check = waste_type_service.get_waste_type_by_name(db=db, name=waste_type_in.name)
        if name_check and name_check.waste_type_id != waste_type_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Waste type '{waste_type_in.name.strip().upper()}' already exists",
            )
    updated = waste_type_service.update_waste_type(
        db=db,
        waste_type=waste_type,
        waste_type_in=waste_type_in,
    )
    return WasteTypeRead.model_validate(updated)
