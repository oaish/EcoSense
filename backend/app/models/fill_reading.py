import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.bin import Bin


class BinFillReading(Base):
    __tablename__ = "bin_fill_readings"
    __table_args__ = (
        CheckConstraint(
            "fill_percentage >= 0 AND fill_percentage <= 100",
            name="valid_fill_percentage",
        ),
        Index("ix_bin_fill_readings_bin_id_recorded_at", "bin_id", "recorded_at"),
    )

    reading_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    bin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("bins.bin_id"),
        nullable=False,
        index=True,
    )
    fill_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(30),
        default="MANUAL",
        server_default=text("'MANUAL'"),
        nullable=False,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    bin: Mapped["Bin"] = relationship(
        "Bin",
        back_populates="fill_readings",
        lazy="joined",
    )
