import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
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
    from app.models.collection import CollectionRecord
    from app.models.user import User


class ProcessingRecord(Base):
    __tablename__ = "processing_records"
    __table_args__ = (
        CheckConstraint(
            "quantity_kg > 0",
            name="positive_processing_quantity",
        ),
        CheckConstraint(
            "processing_type IN ('RECYCLING', 'COMPOSTING')",
            name="valid_processing_type",
        ),
        CheckConstraint(
            "status IN ('COMPLETED', 'PARTIALLY_PROCESSED', 'REJECTED')",
            name="valid_processing_status",
        ),
    )

    processing_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    collection_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("collection_records.collection_id"),
        nullable=False,
        index=True,
    )
    processing_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    quantity_kg: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    processed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="COMPLETED",
        server_default=text("'COMPLETED'"),
        nullable=False,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    collection: Mapped["CollectionRecord"] = relationship(
        "CollectionRecord",
        back_populates="processing_records",
        lazy="joined",
    )
    processor: Mapped["User"] = relationship(
        "User",
        back_populates="processing_records",
        lazy="joined",
    )
