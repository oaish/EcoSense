"""Migration 0009: Add collector_attendance and collection_tasks tables

Revision ID: 0009_collector_attendance_tasks
Revises: 0008_gamification_rewards
Create Date: 2026-10-13 01:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0009_collector_attendance_tasks"
down_revision: Union[str, None] = "0008_gamification_rewards"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create collector_attendance table
    op.create_table(
        "collector_attendance",
        sa.Column("attendance_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("collector_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("check_in_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("check_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'ACTIVE'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED')",
            name=op.f("ck_collector_attendance_valid_attendance_status"),
        ),
        sa.CheckConstraint(
            "check_out_at IS NULL OR check_out_at >= check_in_at",
            name=op.f("ck_collector_attendance_valid_checkout_timestamp"),
        ),
        sa.ForeignKeyConstraint(
            ["collector_id"],
            ["users.user_id"],
            name=op.f("fk_collector_attendance_collector_id_users"),
        ),
        sa.PrimaryKeyConstraint("attendance_id", name=op.f("pk_collector_attendance")),
    )
    op.create_index(op.f("ix_collector_attendance_collector_id"), "collector_attendance", ["collector_id"], unique=False)
    op.create_index(op.f("ix_collector_attendance_attendance_date"), "collector_attendance", ["attendance_date"], unique=False)
    op.create_index(op.f("ix_collector_attendance_status"), "collector_attendance", ["status"], unique=False)
    op.create_index("ix_collector_attendance_collector_date", "collector_attendance", ["collector_id", "attendance_date"], unique=False)

    # 2. Create collection_tasks table
    op.create_table(
        "collection_tasks",
        sa.Column("task_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("task_type", sa.String(length=30), nullable=False),
        sa.Column("collector_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("report_id", sa.BigInteger(), nullable=True),
        sa.Column("priority", sa.String(length=20), server_default=sa.text("'MEDIUM'"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'ASSIGNED'"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("collection_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "task_type IN ('COLLECTION', 'INSPECTION', 'ISSUE_RESPONSE')",
            name=op.f("ck_collection_tasks_valid_task_type"),
        ),
        sa.CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name=op.f("ck_collection_tasks_valid_task_priority"),
        ),
        sa.CheckConstraint(
            "status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name=op.f("ck_collection_tasks_valid_task_status"),
        ),
        sa.ForeignKeyConstraint(
            ["collector_id"],
            ["users.user_id"],
            name=op.f("fk_collection_tasks_collector_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f("fk_collection_tasks_created_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_collection_tasks_bin_id_bins"),
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.location_id"],
            name=op.f("fk_collection_tasks_location_id_locations"),
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["waste_reports.report_id"],
            name=op.f("fk_collection_tasks_report_id_waste_reports"),
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collection_records.collection_id"],
            name=op.f("fk_collection_tasks_collection_id_collection_records"),
        ),
        sa.PrimaryKeyConstraint("task_id", name=op.f("pk_collection_tasks")),
    )
    op.create_index(op.f("ix_collection_tasks_collector_id"), "collection_tasks", ["collector_id"], unique=False)
    op.create_index(op.f("ix_collection_tasks_status"), "collection_tasks", ["status"], unique=False)
    op.create_index(op.f("ix_collection_tasks_task_type"), "collection_tasks", ["task_type"], unique=False)
    op.create_index(op.f("ix_collection_tasks_bin_id"), "collection_tasks", ["bin_id"], unique=False)
    op.create_index(op.f("ix_collection_tasks_location_id"), "collection_tasks", ["location_id"], unique=False)
    op.create_index(op.f("ix_collection_tasks_report_id"), "collection_tasks", ["report_id"], unique=False)
    op.create_index(op.f("ix_collection_tasks_collection_id"), "collection_tasks", ["collection_id"], unique=False)
    op.create_index(op.f("ix_collection_tasks_due_date"), "collection_tasks", ["due_date"], unique=False)
    op.create_index(op.f("ix_collection_tasks_created_at"), "collection_tasks", ["created_at"], unique=False)
    op.create_index("ix_collection_tasks_collector_status", "collection_tasks", ["collector_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_collection_tasks_collector_status", table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_created_at"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_due_date"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_collection_id"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_report_id"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_location_id"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_bin_id"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_task_type"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_status"), table_name="collection_tasks")
    op.drop_index(op.f("ix_collection_tasks_collector_id"), table_name="collection_tasks")
    op.drop_table("collection_tasks")

    op.drop_index("ix_collector_attendance_collector_date", table_name="collector_attendance")
    op.drop_index(op.f("ix_collector_attendance_status"), table_name="collector_attendance")
    op.drop_index(op.f("ix_collector_attendance_attendance_date"), table_name="collector_attendance")
    op.drop_index(op.f("ix_collector_attendance_collector_id"), table_name="collector_attendance")
    op.drop_table("collector_attendance")
