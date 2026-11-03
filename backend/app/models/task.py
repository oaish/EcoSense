import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
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
    from app.models.bin import Bin
    from app.models.collection import CollectionRecord
    from app.models.location import Location
    from app.models.notification import TaskNotification
    from app.models.report import WasteReport
    from app.models.user import User


class CollectionTask(Base):
    __tablename__ = "collection_tasks"
    __table_args__ = (
        CheckConstraint(
            "task_type IN ('COLLECTION', 'INSPECTION', 'ISSUE_RESPONSE')",
            name="valid_task_type",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="valid_task_priority",
        ),
        CheckConstraint(
            "status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="valid_task_status",
        ),
        Index("ix_collection_tasks_collector_status", "collector_id", "status"),
        Index("ix_collection_tasks_created_at", "created_at"),
        Index("ix_collection_tasks_due_date", "due_date"),
    )

    task_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    task_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    collector_id: Mapped[uuid.UUID] = mapped_column(
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
    location_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("locations.location_id"),
        nullable=True,
        index=True,
    )
    report_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("waste_reports.report_id"),
        nullable=True,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    instructions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="ASSIGNED",
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completion_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    collection_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("collection_records.collection_id"),
        nullable=True,
        index=True,
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
        foreign_keys=[collector_id],
        back_populates="assigned_tasks",
        lazy="joined",
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined",
    )
    bin: Mapped[Optional["Bin"]] = relationship(
        "Bin",
        lazy="joined",
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        lazy="joined",
    )
    report: Mapped[Optional["WasteReport"]] = relationship(
        "WasteReport",
        back_populates="tasks",
        lazy="joined",
    )
    collection_record: Mapped[Optional["CollectionRecord"]] = relationship(
        "CollectionRecord",
        lazy="joined",
    )
    notifications: Mapped[List["TaskNotification"]] = relationship(
        "TaskNotification",
        back_populates="task",
        cascade="all, delete-orphan",
    )
