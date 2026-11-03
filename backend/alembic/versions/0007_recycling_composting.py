"""Migration 0007: Add processing_records table for recycling and composting

Revision ID: 0007_recycling_composting
Revises: 0006_fill_predictions
Create Date: 2026-09-20 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0007_recycling_composting"
down_revision: Union[str, None] = "0006_fill_predictions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "processing_records",
        sa.Column("processing_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("collection_id", sa.BigInteger(), nullable=False),
        sa.Column("processing_type", sa.String(length=30), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(precision=8, scale=3), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'COMPLETED'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "quantity_kg > 0",
            name=op.f("ck_processing_records_positive_processing_quantity"),
        ),
        sa.CheckConstraint(
            "processing_type IN ('RECYCLING', 'COMPOSTING')",
            name=op.f("ck_processing_records_valid_processing_type"),
        ),
        sa.CheckConstraint(
            "status IN ('COMPLETED', 'PARTIALLY_PROCESSED', 'REJECTED')",
            name=op.f("ck_processing_records_valid_processing_status"),
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collection_records.collection_id"],
            name=op.f("fk_processing_records_collection_id_collection_records"),
        ),
        sa.ForeignKeyConstraint(
            ["processed_by"],
            ["users.user_id"],
            name=op.f("fk_processing_records_processed_by_users"),
        ),
        sa.PrimaryKeyConstraint("processing_id", name=op.f("pk_processing_records")),
    )
    op.create_index(op.f("ix_processing_records_collection_id"), "processing_records", ["collection_id"], unique=False)
    op.create_index(op.f("ix_processing_records_processed_by"), "processing_records", ["processed_by"], unique=False)
    op.create_index(op.f("ix_processing_records_processing_type"), "processing_records", ["processing_type"], unique=False)
    op.create_index(op.f("ix_processing_records_status"), "processing_records", ["status"], unique=False)
    op.create_index(op.f("ix_processing_records_processed_at"), "processing_records", ["processed_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_processing_records_processed_at"), table_name="processing_records")
    op.drop_index(op.f("ix_processing_records_status"), table_name="processing_records")
    op.drop_index(op.f("ix_processing_records_processing_type"), table_name="processing_records")
    op.drop_index(op.f("ix_processing_records_processed_by"), table_name="processing_records")
    op.drop_index(op.f("ix_processing_records_collection_id"), table_name="processing_records")
    op.drop_table("processing_records")
