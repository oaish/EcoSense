from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


def create_location(db: Session, location_in: LocationCreate) -> Location:
    location = Location(
        name=location_in.name.strip(),
        location_type=location_in.location_type.strip(),
        building=location_in.building.strip() if location_in.building else None,
        floor=location_in.floor.strip() if location_in.floor else None,
        latitude=location_in.latitude,
        longitude=location_in.longitude,
        description=location_in.description,
        is_active=True,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def get_location(db: Session, location_id: int) -> Optional[Location]:
    return db.get(Location, location_id)


def list_locations(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None,
) -> List[Location]:
    statement = select(Location).order_by(Location.location_id)
    if is_active is not None:
        statement = statement.where(Location.is_active == is_active)
    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_location(
    db: Session,
    location: Location,
    location_in: LocationUpdate,
) -> Location:
    update_data = location_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            setattr(location, field, value.strip())
        else:
            setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location


def deactivate_location(db: Session, location: Location) -> Location:
    location.is_active = False
    db.commit()
    db.refresh(location)
    return location
