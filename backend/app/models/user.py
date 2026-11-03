import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, Uuid, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attendance import CollectorAttendance
    from app.models.classification import WasteClassification
    from app.models.collection import CollectionRecord
    from app.models.device_token import DeviceToken
    from app.models.disposal import DisposalRecord
    from app.models.gamification import PointTransaction, RewardRedemption
    from app.models.notification import TaskNotification
    from app.models.processing import ProcessingRecord
    from app.models.report import WasteReport
    from app.models.role import Role
    from app.models.task import CollectionTask


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    role_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        ForeignKey("roles.role_id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )
    push_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        lazy="joined",
    )
    disposal_records: Mapped[List["DisposalRecord"]] = relationship(
        "DisposalRecord",
        back_populates="user",
    )
    reports: Mapped[List["WasteReport"]] = relationship(
        "WasteReport",
        foreign_keys="WasteReport.user_id",
        back_populates="user",
    )
    resolved_reports: Mapped[List["WasteReport"]] = relationship(
        "WasteReport",
        foreign_keys="WasteReport.resolved_by",
        back_populates="resolver",
    )
    collection_records: Mapped[List["CollectionRecord"]] = relationship(
        "CollectionRecord",
        back_populates="collector",
    )
    classifications: Mapped[List["WasteClassification"]] = relationship(
        "WasteClassification",
        back_populates="user",
    )
    processing_records: Mapped[List["ProcessingRecord"]] = relationship(
        "ProcessingRecord",
        back_populates="processor",
    )
    point_transactions: Mapped[List["PointTransaction"]] = relationship(
        "PointTransaction",
        foreign_keys="PointTransaction.user_id",
        back_populates="user",
    )
    reward_redemptions: Mapped[List["RewardRedemption"]] = relationship(
        "RewardRedemption",
        foreign_keys="RewardRedemption.user_id",
        back_populates="user",
    )
    attendance_records: Mapped[List["CollectorAttendance"]] = relationship(
        "CollectorAttendance",
        back_populates="collector",
    )
    assigned_tasks: Mapped[List["CollectionTask"]] = relationship(
        "CollectionTask",
        foreign_keys="CollectionTask.collector_id",
        back_populates="collector",
    )
    notifications: Mapped[List["TaskNotification"]] = relationship(
        "TaskNotification",
        foreign_keys="TaskNotification.recipient_user_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )
    device_tokens: Mapped[List["DeviceToken"]] = relationship(
        "DeviceToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
