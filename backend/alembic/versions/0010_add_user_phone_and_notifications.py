"""Migration 0010: Add user phone_number and task_notifications table

Revision ID: 0010_user_phone_and_notifications
Revises: 0009_collector_attendance_tasks
Create Date: 2026-10-13 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0010_collector_phone_sms"
down_revision: Union[str, None] = "0009_collector_attendance_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add phone_number column to users table
    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(length=20), nullable=True),
    )

    # 2. Create task_notifications audit table
    op.create_table(
        "task_notifications",
        sa.Column("notification_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("recipient_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(length=20), server_default="SMS", nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("provider_msg_id", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["collection_tasks.task_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recipient_user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index("ix_task_notifications_task_id", "task_notifications", ["task_id"])
    op.create_index("ix_task_notifications_recipient_user_id", "task_notifications", ["recipient_user_id"])
    op.create_index("ix_task_notifications_status", "task_notifications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_task_notifications_status", table_name="task_notifications")
    op.drop_index("ix_task_notifications_recipient_user_id", table_name="task_notifications")
    op.drop_index("ix_task_notifications_task_id", table_name="task_notifications")
    op.drop_table("task_notifications")
    op.drop_column("users", "phone_number")
