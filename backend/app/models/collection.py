import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.bin import Bin
    from app.models.processing import ProcessingRecord
    from app.models.user import User


class CollectionRecord(Base):
    __tablename__ = "collection_records"
    __table_args__ = (
        CheckConstraint(
            "(fill_level_before IS NULL) OR (fill_level_before >= 0 AND fill_level_before <= 100)",
            name="valid_fill_before",
        ),
        CheckConstraint(
            "(fill_level_after IS NULL) OR (fill_level_after >= 0 AND fill_level_after <= 100)",
            name="valid_fill_after",
        ),
        CheckConstraint(
            "(collected_quantity_kg IS NULL) OR (collected_quantity_kg > 0)",
            name="positive_collected_quantity",
        ),
        Index("ix_collection_records_bin_id_collected_at", "bin_id", "collected_at"),
    )

    collection_id: Mapped[int] = mapped_column(
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
    collector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    fill_level_before: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    collected_quantity_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True,
    )
    fill_level_after: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    bin: Mapped["Bin"] = relationship(
        "Bin",
        back_populates="collection_records",
        lazy="joined",
    )
    collector: Mapped["User"] = relationship(
        "User",
        back_populates="collection_records",
        lazy="joined",
    )
    processing_records: Mapped[List["ProcessingRecord"]] = relationship(
        "ProcessingRecord",
        back_populates="collection",
    )
