"""Migration 0011: Add device_tokens table and evolve task_notifications for FCM push

Revision ID: 0011_device_tokens_fcm
Revises: 0010_collector_phone_sms
Create Date: 2026-10-13 03:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0011_device_tokens_fcm"
down_revision: Union[str, None] = "0010_collector_phone_sms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add push_notifications_enabled to users table
    op.add_column(
        "users",
        sa.Column(
            "push_notifications_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # 2. Evolve task_notifications table to be omni-channel
    # Make task_id nullable so non-task notifications can also be recorded
    op.alter_column(
        "task_notifications",
        "task_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # Add report_id, notification_type, title, body columns
    op.add_column(
        "task_notifications",
        sa.Column("report_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_task_notifications_report_id_waste_reports",
        "task_notifications",
        "waste_reports",
        ["report_id"],
        ["report_id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_task_notifications_report_id",
        "task_notifications",
        ["report_id"],
    )

    op.add_column(
        "task_notifications",
        sa.Column("notification_type", sa.String(length=50), nullable=True),
    )
    op.create_index(
        "ix_task_notifications_notification_type",
        "task_notifications",
        ["notification_type"],
    )

    op.add_column(
        "task_notifications",
        sa.Column("title", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "task_notifications",
        sa.Column("body", sa.Text(), nullable=True),
    )

    # Update server default for channel to 'PUSH' while keeping historical rows as 'SMS'
    op.alter_column(
        "task_notifications",
        "channel",
        server_default="PUSH",
    )

    # 3. Create device_tokens table
    op.create_table(
        "device_tokens",
        sa.Column("token_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fcm_token", sa.String(length=512), nullable=False),
        sa.Column("device_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_id"),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])
    op.create_index("ix_device_tokens_fcm_token", "device_tokens", ["fcm_token"], unique=True)
    op.create_index("ix_device_tokens_is_active", "device_tokens", ["is_active"])


def downgrade() -> None:
    # 1. Drop device_tokens table
    op.drop_index("ix_device_tokens_is_active", table_name="device_tokens")
    op.drop_index("ix_device_tokens_fcm_token", table_name="device_tokens")
    op.drop_index("ix_device_tokens_user_id", table_name="device_tokens")
    op.drop_table("device_tokens")

    # 2. Revert task_notifications
    op.alter_column(
        "task_notifications",
        "channel",
        server_default="SMS",
    )
    op.drop_column("task_notifications", "body")
    op.drop_column("task_notifications", "title")
    op.drop_index("ix_task_notifications_notification_type", table_name="task_notifications")
    op.drop_column("task_notifications", "notification_type")
    op.drop_index("ix_task_notifications_report_id", table_name="task_notifications")
    op.drop_constraint("fk_task_notifications_report_id_waste_reports", "task_notifications", type_="foreignkey")
    op.drop_column("task_notifications", "report_id")
    op.alter_column(
        "task_notifications",
        "task_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 3. Drop push_notifications_enabled
    op.drop_column("users", "push_notifications_enabled")
