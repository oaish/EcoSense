"""Initial migration: pgcrypto extension, roles and users tables

Revision ID: 0001_roles_users
Revises: 
Create Date: 2026-09-18 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_roles_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ensure pgcrypto extension is available for gen_random_uuid()
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))

    # 2. Create roles table
    op.create_table(
        "roles",
        sa.Column("role_id", sa.SmallInteger(), autoincrement=True, nullable=False),
        sa.Column("role_name", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("role_id", name=op.f("pk_roles")),
        sa.UniqueConstraint("role_name", name=op.f("uq_roles_role_name")),
    )
    op.create_index(op.f("ix_roles_role_name"), "roles", ["role_name"], unique=True)

    # 3. Create users table
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role_id", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.role_id"],
            name=op.f("fk_users_role_id_roles"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role_id"), "users", ["role_id"], unique=False)

    # 4. Seed initial roles
    roles_table = sa.table(
        "roles",
        sa.column("role_name", sa.String),
    )
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO roles (role_name)
                VALUES ('STUDENT'), ('STAFF'), ('COLLECTOR'), ('ADMIN')
                ON CONFLICT (role_name) DO NOTHING;
                """
            )
        )
    else:
        op.bulk_insert(
            roles_table,
            [
                {"role_name": "STUDENT"},
                {"role_name": "STAFF"},
                {"role_name": "COLLECTOR"},
                {"role_name": "ADMIN"},
            ],
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_role_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_roles_role_name"), table_name="roles")
    op.drop_table("roles")
