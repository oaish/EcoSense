from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services import location_service

router = APIRouter()


@router.post(
    "",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Location",
    description="Create a new physical campus location (ADMIN only).",
)
def create_location(
    location_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> LocationRead:
    location = location_service.create_location(db=db, location_in=location_in)
    return LocationRead.model_validate(location)


@router.get(
    "",
    response_model=List[LocationRead],
    summary="List Locations",
    description="Retrieve campus locations with pagination and active-state filtering.",
)
def list_locations(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[LocationRead]:
    locations = location_service.list_locations(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )
    return [LocationRead.model_validate(loc) for loc in locations]


@router.get(
    "/{location_id}",
    response_model=LocationRead,
    summary="Get Location by ID",
    description="Retrieve details of a single campus location.",
)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LocationRead:
    location = location_service.get_location(db=db, location_id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found",
        )
    return LocationRead.model_validate(location)


@router.patch(
    "/{location_id}",
    response_model=LocationRead,
    summary="Update Location",
    description="Update a campus location or deactivate it (ADMIN only).",
)
def update_location(
    location_id: int,
    location_in: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> LocationRead:
    location = location_service.get_location(db=db, location_id=location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found",
        )
    updated = location_service.update_location(
        db=db,
        location=location,
        location_in=location_in,
    )
    return LocationRead.model_validate(updated)
