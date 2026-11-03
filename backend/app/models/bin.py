import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.collection import CollectionRecord
    from app.models.disposal import DisposalRecord
    from app.models.fill_reading import BinFillReading
    from app.models.location import Location
    from app.models.prediction import FillPrediction
    from app.models.report import WasteReport
    from app.models.waste_type import WasteType


class Bin(Base):
    __tablename__ = "bins"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'FULL', 'DAMAGED', 'MISSING', 'INACTIVE')",
            name="valid_bin_status",
        ),
        CheckConstraint(
            "(current_fill_percentage IS NULL) OR (current_fill_percentage >= 0 AND current_fill_percentage <= 100)",
            name="valid_fill_percentage",
        ),
    )

    bin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    bin_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("locations.location_id"),
        nullable=False,
        index=True,
    )
    waste_type_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        ForeignKey("waste_types.waste_type_id"),
        nullable=False,
        index=True,
    )
    capacity_litres: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2),
        nullable=True,
    )
    qr_token: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
    )
    current_fill_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        server_default=text("'ACTIVE'"),
        nullable=False,
    )
    installed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="bins",
        lazy="joined",
    )
    waste_type: Mapped["WasteType"] = relationship(
        "WasteType",
        back_populates="bins",
        lazy="joined",
    )
    disposal_records: Mapped[List["DisposalRecord"]] = relationship(
        "DisposalRecord",
        back_populates="bin",
    )
    reports: Mapped[List["WasteReport"]] = relationship(
        "WasteReport",
        back_populates="bin",
    )
    fill_readings: Mapped[List["BinFillReading"]] = relationship(
        "BinFillReading",
        back_populates="bin",
    )
    collection_records: Mapped[List["CollectionRecord"]] = relationship(
        "CollectionRecord",
        back_populates="bin",
    )
    predictions: Mapped[List["FillPrediction"]] = relationship(
        "FillPrediction",
        back_populates="bin",
    )
