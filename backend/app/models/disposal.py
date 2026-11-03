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
    from app.models.classification import WasteClassification
    from app.models.user import User


class DisposalRecord(Base):
    __tablename__ = "disposal_records"
    __table_args__ = (
        CheckConstraint(
            "(quantity_kg IS NULL) OR (quantity_kg > 0)",
            name="positive_disposal_quantity",
        ),
    )

    disposal_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    bin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("bins.bin_id"),
        nullable=False,
        index=True,
    )
    quantity_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 3),
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="disposal_records",
        lazy="joined",
    )
    bin: Mapped["Bin"] = relationship(
        "Bin",
        back_populates="disposal_records",
        lazy="joined",
    )
    classifications: Mapped[List["WasteClassification"]] = relationship(
        "WasteClassification",
        back_populates="disposal",
    )
