"""Migration 0002: Add locations, waste_types, and bins tables

Revision ID: 0002_locations_waste_types_bins
Revises: 0001_roles_users
Create Date: 2026-09-18 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_locations_waste_types_bins"
down_revision: Union[str, None] = "0001_roles_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Create locations table
    op.create_table(
        "locations",
        sa.Column("location_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("location_type", sa.String(length=50), nullable=False),
        sa.Column("building", sa.String(length=100), nullable=True),
        sa.Column("floor", sa.String(length=30), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("location_id", name=op.f("pk_locations")),
    )
    op.create_index(op.f("ix_locations_name"), "locations", ["name"], unique=False)

    # 2. Create waste_types table
    op.create_table(
        "waste_types",
        sa.Column("waste_type_id", sa.SmallInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("waste_type_id", name=op.f("pk_waste_types")),
        sa.UniqueConstraint("name", name=op.f("uq_waste_types_name")),
    )
    op.create_index(op.f("ix_waste_types_name"), "waste_types", ["name"], unique=True)

    # Seed initial 6 waste types
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO waste_types (name, description, is_active)
                VALUES
                    ('WET_ORGANIC', 'Organic and wet waste', true),
                    ('DRY_RECYCLABLE', 'Dry recyclable waste', true),
                    ('PAPER', 'Paper waste', true),
                    ('METAL', 'Metal waste', true),
                    ('E_WASTE', 'Electronic waste', true),
                    ('GARDEN', 'Garden and landscaping waste', true)
                ON CONFLICT (name) DO NOTHING;
                """
            )
        )
    else:
        waste_types_table = sa.table(
            "waste_types",
            sa.column("name", sa.String),
            sa.column("description", sa.Text),
            sa.column("is_active", sa.Boolean),
        )
        op.bulk_insert(
            waste_types_table,
            [
                {"name": "WET_ORGANIC", "description": "Organic and wet waste", "is_active": True},
                {"name": "DRY_RECYCLABLE", "description": "Dry recyclable waste", "is_active": True},
                {"name": "PAPER", "description": "Paper waste", "is_active": True},
                {"name": "METAL", "description": "Metal waste", "is_active": True},
                {"name": "E_WASTE", "description": "Electronic waste", "is_active": True},
                {"name": "GARDEN", "description": "Garden and landscaping waste", "is_active": True},
            ],
        )

    # 3. Create bins table
    op.create_table(
        "bins",
        sa.Column(
            "bin_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("bin_code", sa.String(length=50), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=False),
        sa.Column("waste_type_id", sa.SmallInteger(), nullable=False),
        sa.Column("capacity_litres", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column(
            "qr_token",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("current_fill_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'ACTIVE'"), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'FULL', 'DAMAGED', 'MISSING', 'INACTIVE')",
            name=op.f("ck_bins_valid_bin_status"),
        ),
        sa.CheckConstraint(
            "(current_fill_percentage IS NULL) OR (current_fill_percentage >= 0 AND current_fill_percentage <= 100)",
            name=op.f("ck_bins_valid_fill_percentage"),
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.location_id"],
            name=op.f("fk_bins_location_id_locations"),
        ),
        sa.ForeignKeyConstraint(
            ["waste_type_id"],
            ["waste_types.waste_type_id"],
            name=op.f("fk_bins_waste_type_id_waste_types"),
        ),
        sa.PrimaryKeyConstraint("bin_id", name=op.f("pk_bins")),
        sa.UniqueConstraint("bin_code", name=op.f("uq_bins_bin_code")),
        sa.UniqueConstraint("qr_token", name=op.f("uq_bins_qr_token")),
    )
    op.create_index(op.f("ix_bins_bin_code"), "bins", ["bin_code"], unique=True)
    op.create_index(op.f("ix_bins_location_id"), "bins", ["location_id"], unique=False)
    op.create_index(op.f("ix_bins_waste_type_id"), "bins", ["waste_type_id"], unique=False)
    op.create_index(op.f("ix_bins_qr_token"), "bins", ["qr_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_bins_qr_token"), table_name="bins")
    op.drop_index(op.f("ix_bins_waste_type_id"), table_name="bins")
    op.drop_index(op.f("ix_bins_location_id"), table_name="bins")
    op.drop_index(op.f("ix_bins_bin_code"), table_name="bins")
    op.drop_table("bins")
    op.drop_index(op.f("ix_waste_types_name"), table_name="waste_types")
    op.drop_table("waste_types")
    op.drop_index(op.f("ix_locations_name"), table_name="locations")
    op.drop_table("locations")
