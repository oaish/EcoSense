import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class CollectorAttendance(Base):
    __tablename__ = "collector_attendance"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED')",
            name="valid_attendance_status",
        ),
        CheckConstraint(
            "check_out_at IS NULL OR check_out_at >= check_in_at",
            name="valid_checkout_timestamp",
        ),
        Index("ix_collector_attendance_collector_date", "collector_id", "attendance_date"),
        Index("ix_collector_attendance_status", "status"),
    )

    attendance_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    collector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    check_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    check_out_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        nullable=False,
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    collector: Mapped["User"] = relationship(
        "User",
        back_populates="attendance_records",
        lazy="joined",
    )
