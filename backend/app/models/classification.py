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
    SmallInteger,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.disposal import DisposalRecord
    from app.models.user import User
    from app.models.waste_type import WasteType


class WasteClassification(Base):
    __tablename__ = "waste_classifications"
    __table_args__ = (
        CheckConstraint(
            "(confidence_score IS NULL) OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="valid_confidence_score",
        ),
    )

    classification_id: Mapped[int] = mapped_column(
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
    disposal_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("disposal_records.disposal_id"),
        nullable=True,
        index=True,
    )
    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    predicted_waste_type_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        ForeignKey("waste_types.waste_type_id"),
        nullable=False,
        index=True,
    )
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )
    model_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="classifications",
        lazy="joined",
    )
    disposal: Mapped[Optional["DisposalRecord"]] = relationship(
        "DisposalRecord",
        back_populates="classifications",
        lazy="joined",
    )
    predicted_waste_type: Mapped["WasteType"] = relationship(
        "WasteType",
        back_populates="classifications",
        lazy="joined",
    )
