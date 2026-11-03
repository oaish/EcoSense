import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
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
    from app.models.user import User


class PointTransaction(Base):
    __tablename__ = "point_transactions"
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('EARN', 'REDEEM', 'ADJUSTMENT')",
            name="valid_transaction_type",
        ),
        CheckConstraint(
            "(transaction_type = 'EARN' AND points > 0) OR "
            "(transaction_type = 'REDEEM' AND points < 0) OR "
            "(transaction_type = 'ADJUSTMENT' AND points != 0)",
            name="valid_transaction_points",
        ),
        Index("ix_point_transactions_source", "source_type", "source_id"),
        Index(
            "ix_point_transactions_unique_earn_source",
            "source_type",
            "source_id",
            "transaction_type",
            unique=True,
            sqlite_where=text("transaction_type = 'EARN' AND source_id IS NOT NULL"),
            postgresql_where=text("transaction_type = 'EARN' AND source_id IS NOT NULL"),
        ),
    )

    transaction_id: Mapped[int] = mapped_column(
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
    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="point_transactions",
        lazy="joined",
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined",
    )


class PointRule(Base):
    __tablename__ = "point_rules"
    __table_args__ = (
        CheckConstraint("points > 0", name="positive_rule_points"),
    )

    rule_id: Mapped[int] = mapped_column(
        SmallInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    action_type: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
        index=True,
    )
    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
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


class Reward(Base):
    __tablename__ = "rewards"
    __table_args__ = (
        CheckConstraint("points_cost > 0", name="positive_reward_points_cost"),
        CheckConstraint(
            "(stock_quantity IS NULL) OR (stock_quantity >= 0)",
            name="non_negative_stock_quantity",
        ),
    )

    reward_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    points_cost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    stock_quantity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
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

    redemptions: Mapped[List["RewardRedemption"]] = relationship(
        "RewardRedemption",
        back_populates="reward",
    )


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"
    __table_args__ = (
        CheckConstraint("points_spent > 0", name="positive_points_spent"),
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'FULFILLED', 'CANCELLED')",
            name="valid_redemption_status",
        ),
    )

    redemption_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    reward_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("rewards.reward_id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True).with_variant(Uuid(), "sqlite"),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )
    points_spent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        server_default=text("'PENDING'"),
        nullable=False,
        index=True,
    )
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    reward: Mapped["Reward"] = relationship(
        "Reward",
        back_populates="redemptions",
        lazy="joined",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="reward_redemptions",
        lazy="joined",
    )
