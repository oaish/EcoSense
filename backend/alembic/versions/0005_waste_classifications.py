"""Migration 0005: Add waste_classifications table

Revision ID: 0005_waste_classifications
Revises: 0004_fill_collections
Create Date: 2026-09-18 04:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_waste_classifications"
down_revision: Union[str, None] = "0004_fill_collections"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waste_classifications",
        sa.Column("classification_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("disposal_id", sa.BigInteger(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("predicted_waste_type_id", sa.SmallInteger(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "(confidence_score IS NULL) OR (confidence_score >= 0 AND confidence_score <= 1)",
            name=op.f("ck_waste_classifications_valid_confidence_score"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_waste_classifications_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["disposal_id"],
            ["disposal_records.disposal_id"],
            name=op.f("fk_waste_classifications_disposal_id_disposal_records"),
        ),
        sa.ForeignKeyConstraint(
            ["predicted_waste_type_id"],
            ["waste_types.waste_type_id"],
            name=op.f("fk_waste_classifications_predicted_waste_type_id_waste_types"),
        ),
        sa.PrimaryKeyConstraint("classification_id", name=op.f("pk_waste_classifications")),
    )
    op.create_index(op.f("ix_waste_classifications_user_id"), "waste_classifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_waste_classifications_disposal_id"), "waste_classifications", ["disposal_id"], unique=False)
    op.create_index(op.f("ix_waste_classifications_predicted_waste_type_id"), "waste_classifications", ["predicted_waste_type_id"], unique=False)
    op.create_index(op.f("ix_waste_classifications_created_at"), "waste_classifications", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_waste_classifications_created_at"), table_name="waste_classifications")
    op.drop_index(op.f("ix_waste_classifications_predicted_waste_type_id"), table_name="waste_classifications")
    op.drop_index(op.f("ix_waste_classifications_disposal_id"), table_name="waste_classifications")
    op.drop_index(op.f("ix_waste_classifications_user_id"), table_name="waste_classifications")
    op.drop_table("waste_classifications")
