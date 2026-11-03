"""Migration 0004: Add bin_fill_readings and collection_records tables

Revision ID: 0004_fill_collections
Revises: 0003_disposals_and_reports
Create Date: 2026-09-18 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_fill_collections"
down_revision: Union[str, None] = "0003_disposals_and_reports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create bin_fill_readings table
    op.create_table(
        "bin_fill_readings",
        sa.Column("reading_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fill_percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("source", sa.String(length=30), server_default=sa.text("'MANUAL'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "fill_percentage >= 0 AND fill_percentage <= 100",
            name=op.f("ck_bin_fill_readings_valid_fill_percentage"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_bin_fill_readings_bin_id_bins"),
        ),
        sa.PrimaryKeyConstraint("reading_id", name=op.f("pk_bin_fill_readings")),
    )
    op.create_index(op.f("ix_bin_fill_readings_bin_id"), "bin_fill_readings", ["bin_id"], unique=False)
    op.create_index(op.f("ix_bin_fill_readings_recorded_at"), "bin_fill_readings", ["recorded_at"], unique=False)
    op.create_index("ix_bin_fill_readings_bin_id_recorded_at", "bin_fill_readings", ["bin_id", "recorded_at"], unique=False)

    # 2. Create collection_records table
    op.create_table(
        "collection_records",
        sa.Column("collection_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collector_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fill_level_before", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("collected_quantity_kg", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("fill_level_after", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(fill_level_before IS NULL) OR (fill_level_before >= 0 AND fill_level_before <= 100)",
            name=op.f("ck_collection_records_valid_fill_before"),
        ),
        sa.CheckConstraint(
            "(fill_level_after IS NULL) OR (fill_level_after >= 0 AND fill_level_after <= 100)",
            name=op.f("ck_collection_records_valid_fill_after"),
        ),
        sa.CheckConstraint(
            "(collected_quantity_kg IS NULL) OR (collected_quantity_kg > 0)",
            name=op.f("ck_collection_records_positive_collected_quantity"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_collection_records_bin_id_bins"),
        ),
        sa.ForeignKeyConstraint(
            ["collector_id"],
            ["users.user_id"],
            name=op.f("fk_collection_records_collector_id_users"),
        ),
        sa.PrimaryKeyConstraint("collection_id", name=op.f("pk_collection_records")),
    )
    op.create_index(op.f("ix_collection_records_bin_id"), "collection_records", ["bin_id"], unique=False)
    op.create_index(op.f("ix_collection_records_collector_id"), "collection_records", ["collector_id"], unique=False)
    op.create_index(op.f("ix_collection_records_collected_at"), "collection_records", ["collected_at"], unique=False)
    op.create_index("ix_collection_records_bin_id_collected_at", "collection_records", ["bin_id", "collected_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_collection_records_bin_id_collected_at", table_name="collection_records")
    op.drop_index(op.f("ix_collection_records_collected_at"), table_name="collection_records")
    op.drop_index(op.f("ix_collection_records_collector_id"), table_name="collection_records")
    op.drop_index(op.f("ix_collection_records_bin_id"), table_name="collection_records")
    op.drop_table("collection_records")
    op.drop_index("ix_bin_fill_readings_bin_id_recorded_at", table_name="bin_fill_readings")
    op.drop_index(op.f("ix_bin_fill_readings_recorded_at"), table_name="bin_fill_readings")
    op.drop_index(op.f("ix_bin_fill_readings_bin_id"), table_name="bin_fill_readings")
    op.drop_table("bin_fill_readings")
