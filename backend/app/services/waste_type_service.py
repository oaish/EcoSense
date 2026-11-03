from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.waste_type import WasteType
from app.schemas.waste_type import WasteTypeCreate, WasteTypeUpdate


def get_waste_type(db: Session, waste_type_id: int) -> Optional[WasteType]:
    return db.get(WasteType, waste_type_id)


def get_waste_type_by_name(db: Session, name: str) -> Optional[WasteType]:
    statement = select(WasteType).where(WasteType.name == name.strip().upper())
    return db.scalar(statement)


def list_waste_types(db: Session, is_active_only: bool = True) -> List[WasteType]:
    statement = select(WasteType).order_by(WasteType.waste_type_id)
    if is_active_only:
        statement = statement.where(WasteType.is_active.is_(True))
    return list(db.scalars(statement).all())


def create_waste_type(db: Session, waste_type_in: WasteTypeCreate) -> WasteType:
    waste_type = WasteType(
        name=waste_type_in.name.strip().upper(),
        description=waste_type_in.description,
        is_active=True,
    )
    db.add(waste_type)
    db.commit()
    db.refresh(waste_type)
    return waste_type


def update_waste_type(
    db: Session,
    waste_type: WasteType,
    waste_type_in: WasteTypeUpdate,
) -> WasteType:
    update_data = waste_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "name" and isinstance(value, str):
            setattr(waste_type, field, value.strip().upper())
        else:
            setattr(waste_type, field, value)
    db.commit()
    db.refresh(waste_type)
    return waste_type
