"""Migration 0006: Add fill_predictions table

Revision ID: 0006_fill_predictions
Revises: 0005_waste_classifications
Create Date: 2026-09-18 05:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_fill_predictions"
down_revision: Union[str, None] = "0005_waste_classifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fill_predictions",
        sa.Column("prediction_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("predicted_fill_percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("prediction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("target_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("lower_bound", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("upper_bound", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "predicted_fill_percentage >= 0 AND predicted_fill_percentage <= 100",
            name=op.f("ck_fill_predictions_valid_predicted_fill_percentage"),
        ),
        sa.CheckConstraint(
            "(confidence_score IS NULL) OR (confidence_score >= 0 AND confidence_score <= 1)",
            name=op.f("ck_fill_predictions_valid_prediction_confidence_score"),
        ),
        sa.ForeignKeyConstraint(
            ["bin_id"],
            ["bins.bin_id"],
            name=op.f("fk_fill_predictions_bin_id_bins"),
        ),
        sa.PrimaryKeyConstraint("prediction_id", name=op.f("pk_fill_predictions")),
    )
    op.create_index(op.f("ix_fill_predictions_bin_id"), "fill_predictions", ["bin_id"], unique=False)
    op.create_index(op.f("ix_fill_predictions_target_timestamp"), "fill_predictions", ["target_timestamp"], unique=False)
    op.create_index("ix_fill_predictions_bin_id_target", "fill_predictions", ["bin_id", "target_timestamp"], unique=False)
    op.create_index(op.f("ix_fill_predictions_created_at"), "fill_predictions", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fill_predictions_created_at"), table_name="fill_predictions")
    op.drop_index("ix_fill_predictions_bin_id_target", table_name="fill_predictions")
    op.drop_index(op.f("ix_fill_predictions_target_timestamp"), table_name="fill_predictions")
    op.drop_index(op.f("ix_fill_predictions_bin_id"), table_name="fill_predictions")
    op.drop_table("fill_predictions")
