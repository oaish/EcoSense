"""Migration 0003: Add disposal_records and waste_reports tables

Revision ID: 0003_disposals_and_reports
Revises: 0002_locations_waste_types_bins
Create Date: 2026-09-18 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_disposals_and_reports"
down_revision: Union[str, None] = "0002_locations_waste_types_bins"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create disposal_records table
    op.create_table(
        "disposal_records",
        sa.Column("disposal_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(quantity_kg IS NULL) OR (quantity_kg > 0)",
            name=op.f("ck_disposal_records_positive_disposal_quantity"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_disposal_records_bin_id_bins"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_disposal_records_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("disposal_id", name=op.f("pk_disposal_records")),
    )
    op.create_index(op.f("ix_disposal_records_user_id"), "disposal_records", ["user_id"], unique=False)
    op.create_index(op.f("ix_disposal_records_bin_id"), "disposal_records", ["bin_id"], unique=False)
    op.create_index(op.f("ix_disposal_records_recorded_at"), "disposal_records", ["recorded_at"], unique=False)

    # 2. Create waste_reports table
    op.create_table(
        "waste_reports",
        sa.Column("report_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED')",
            name=op.f("ck_waste_reports_valid_report_status"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_waste_reports_bin_id_bins"),
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by"],
            ["users.user_id"],
            name=op.f("fk_waste_reports_resolved_by_users"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_waste_reports_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("report_id", name=op.f("pk_waste_reports")),
    )
    op.create_index(op.f("ix_waste_reports_user_id"), "waste_reports", ["user_id"], unique=False)
    op.create_index(op.f("ix_waste_reports_bin_id"), "waste_reports", ["bin_id"], unique=False)
    op.create_index(op.f("ix_waste_reports_status"), "waste_reports", ["status"], unique=False)
    op.create_index(op.f("ix_waste_reports_created_at"), "waste_reports", ["created_at"], unique=False)
    op.create_index(op.f("ix_waste_reports_report_type"), "waste_reports", ["report_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_waste_reports_report_type"), table_name="waste_reports")
    op.drop_index(op.f("ix_waste_reports_created_at"), table_name="waste_reports")
    op.drop_index(op.f("ix_waste_reports_status"), table_name="waste_reports")
    op.drop_index(op.f("ix_waste_reports_bin_id"), table_name="waste_reports")
    op.drop_index(op.f("ix_waste_reports_user_id"), table_name="waste_reports")
    op.drop_table("waste_reports")
    op.drop_index(op.f("ix_disposal_records_recorded_at"), table_name="disposal_records")
    op.drop_index(op.f("ix_disposal_records_bin_id"), table_name="disposal_records")
    op.drop_index(op.f("ix_disposal_records_user_id"), table_name="disposal_records")
    op.drop_table("disposal_records")
