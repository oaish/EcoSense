import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
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
    from app.models.task import CollectionTask
    from app.models.user import User


class WasteReport(Base):
    __tablename__ = "waste_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED')",
            name="valid_report_status",
        ),
    )

    report_id: Mapped[int] = mapped_column(
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
    bin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("bins.bin_id"),
        nullable=True,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        server_default=text("'PENDING'"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="reports",
        lazy="joined",
    )
    bin: Mapped[Optional["Bin"]] = relationship(
        "Bin",
        back_populates="reports",
        lazy="joined",
    )
    resolver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[resolved_by],
        back_populates="resolved_reports",
        lazy="joined",
    )
    tasks: Mapped[List["CollectionTask"]] = relationship(
        "CollectionTask",
        back_populates="report",
    )
