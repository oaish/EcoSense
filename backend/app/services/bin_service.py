import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.schemas.bin import BinCreate, BinUpdate


def get_bin_by_id(db: Session, bin_id: uuid.UUID) -> Optional[Bin]:
    statement = (
        select(Bin)
        .options(joinedload(Bin.location), joinedload(Bin.waste_type))
        .where(Bin.bin_id == bin_id)
    )
    return db.scalar(statement)


def get_bin_by_code(db: Session, bin_code: str) -> Optional[Bin]:
    statement = (
        select(Bin)
        .options(joinedload(Bin.location), joinedload(Bin.waste_type))
        .where(Bin.bin_code == bin_code.strip().upper())
    )
    return db.scalar(statement)


def get_bin_by_qr_token(db: Session, qr_token: uuid.UUID) -> Optional[Bin]:
    statement = (
        select(Bin)
        .options(joinedload(Bin.location), joinedload(Bin.waste_type))
        .where(Bin.qr_token == qr_token)
    )
    return db.scalar(statement)


def list_bins(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    location_id: Optional[int] = None,
    waste_type_id: Optional[int] = None,
    status: Optional[str] = None,
) -> List[Bin]:
    statement = (
        select(Bin)
        .options(joinedload(Bin.location), joinedload(Bin.waste_type))
        .order_by(Bin.bin_code)
    )
    if location_id is not None:
        statement = statement.where(Bin.location_id == location_id)
    if waste_type_id is not None:
        statement = statement.where(Bin.waste_type_id == waste_type_id)
    if status is not None:
        statement = statement.where(Bin.status == status.strip().upper())

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_bin(db: Session, bin_in: BinCreate) -> Bin:
    bin_obj = Bin(
        bin_code=bin_in.bin_code.strip().upper(),
        location_id=bin_in.location_id,
        waste_type_id=bin_in.waste_type_id,
        capacity_litres=bin_in.capacity_litres,
        installed_at=bin_in.installed_at,
        status="ACTIVE",
    )
    db.add(bin_obj)
    db.commit()
    db.refresh(bin_obj)
    return bin_obj


def update_bin(db: Session, bin_obj: Bin, bin_in: BinUpdate) -> Bin:
    update_data = bin_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and isinstance(value, str):
            setattr(bin_obj, field, value.strip().upper())
        else:
            setattr(bin_obj, field, value)
    db.commit()
    db.refresh(bin_obj)
    return bin_obj
