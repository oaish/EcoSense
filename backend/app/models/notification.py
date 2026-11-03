import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.report import WasteReport
    from app.models.task import CollectionTask
    from app.models.user import User


class TaskNotification(Base):
    """Stores notification dispatch audit records and provider outcomes across channels (Push, SMS)."""

    __tablename__ = "task_notifications"

    notification_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("collection_tasks.task_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    report_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("waste_reports.report_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        default="PUSH",
        server_default="PUSH",
        nullable=False,
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    provider_msg_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    task: Mapped[Optional["CollectionTask"]] = relationship(
        "CollectionTask",
        back_populates="notifications",
    )
    report: Mapped[Optional["WasteReport"]] = relationship(
        "WasteReport",
    )
    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
    )
