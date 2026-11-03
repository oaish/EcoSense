"""Migration 0008: Add gamification, point ledger, point rules, and rewards tables

Revision ID: 0008_gamification_rewards
Revises: 0007_recycling_composting
Create Date: 2026-09-20 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008_gamification_rewards"
down_revision: Union[str, None] = "0007_recycling_composting"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. point_rules table
    point_rules_table = op.create_table(
        "point_rules",
        sa.Column("rule_id", sa.SmallInteger(), autoincrement=True, nullable=False),
        sa.Column("action_type", sa.String(length=40), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points > 0", name=op.f("ck_point_rules_positive_rule_points")),
        sa.PrimaryKeyConstraint("rule_id", name=op.f("pk_point_rules")),
        sa.UniqueConstraint("action_type", name=op.f("uq_point_rules_action_type")),
    )
    op.create_index(op.f("ix_point_rules_action_type"), "point_rules", ["action_type"], unique=True)
    op.create_index(op.f("ix_point_rules_is_active"), "point_rules", ["is_active"], unique=False)

    # 2. point_transactions table (Immutable Points Ledger)
    op.create_table(
        "point_transactions",
        sa.Column("transaction_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "transaction_type IN ('EARN', 'REDEEM', 'ADJUSTMENT')",
            name=op.f("ck_point_transactions_valid_transaction_type"),
        ),
        sa.CheckConstraint(
            "(transaction_type = 'EARN' AND points > 0) OR "
            "(transaction_type = 'REDEEM' AND points < 0) OR "
            "(transaction_type = 'ADJUSTMENT' AND points != 0)",
            name=op.f("ck_point_transactions_valid_transaction_points"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_point_transactions_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.user_id"],
            name=op.f("fk_point_transactions_created_by_users"),
        ),
        sa.PrimaryKeyConstraint("transaction_id", name=op.f("pk_point_transactions")),
    )
    op.create_index(op.f("ix_point_transactions_user_id"), "point_transactions", ["user_id"], unique=False)
    op.create_index(op.f("ix_point_transactions_transaction_type"), "point_transactions", ["transaction_type"], unique=False)
    op.create_index(op.f("ix_point_transactions_source_type"), "point_transactions", ["source_type"], unique=False)
    op.create_index(op.f("ix_point_transactions_created_at"), "point_transactions", ["created_at"], unique=False)
    op.create_index("ix_point_transactions_source", "point_transactions", ["source_type", "source_id"], unique=False)
    op.create_index(
        "ix_point_transactions_unique_earn_source",
        "point_transactions",
        ["source_type", "source_id", "transaction_type"],
        unique=True,
        postgresql_where=sa.text("transaction_type = 'EARN' AND source_id IS NOT NULL"),
    )

    # 3. rewards table
    op.create_table(
        "rewards",
        sa.Column("reward_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("points_cost", sa.Integer(), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points_cost > 0", name=op.f("ck_rewards_positive_reward_points_cost")),
        sa.CheckConstraint(
            "(stock_quantity IS NULL) OR (stock_quantity >= 0)",
            name=op.f("ck_rewards_non_negative_stock_quantity"),
        ),
        sa.PrimaryKeyConstraint("reward_id", name=op.f("pk_rewards")),
    )
    op.create_index(op.f("ix_rewards_is_active"), "rewards", ["is_active"], unique=False)

    # 4. reward_redemptions table
    op.create_table(
        "reward_redemptions",
        sa.Column("redemption_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("reward_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points_spent", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points_spent > 0", name=op.f("ck_reward_redemptions_positive_points_spent")),
        sa.CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'FULFILLED', 'CANCELLED')",
            name=op.f("ck_reward_redemptions_valid_redemption_status"),
        ),
        sa.ForeignKeyConstraint(
            ["reward_id"],
            ["rewards.reward_id"],
            name=op.f("fk_reward_redemptions_reward_id_rewards"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_reward_redemptions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("redemption_id", name=op.f("pk_reward_redemptions")),
    )
    op.create_index(op.f("ix_reward_redemptions_reward_id"), "reward_redemptions", ["reward_id"], unique=False)
    op.create_index(op.f("ix_reward_redemptions_user_id"), "reward_redemptions", ["user_id"], unique=False)
    op.create_index(op.f("ix_reward_redemptions_status"), "reward_redemptions", ["status"], unique=False)
    op.create_index(op.f("ix_reward_redemptions_redeemed_at"), "reward_redemptions", ["redeemed_at"], unique=False)

    # Seed default point rules
    op.bulk_insert(
        point_rules_table,
        [
            {
                "action_type": "DISPOSAL",
                "points": 10,
                "description": "Points awarded for proper waste disposal",
                "is_active": True,
            },
            {
                "action_type": "WASTE_REPORT",
                "points": 5,
                "description": "Points awarded for verified and resolved waste report",
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reward_redemptions_redeemed_at"), table_name="reward_redemptions")
    op.drop_index(op.f("ix_reward_redemptions_status"), table_name="reward_redemptions")
    op.drop_index(op.f("ix_reward_redemptions_user_id"), table_name="reward_redemptions")
    op.drop_index(op.f("ix_reward_redemptions_reward_id"), table_name="reward_redemptions")
    op.drop_table("reward_redemptions")

    op.drop_index(op.f("ix_rewards_is_active"), table_name="rewards")
    op.drop_table("rewards")

    op.drop_index("ix_point_transactions_unique_earn_source", table_name="point_transactions")
    op.drop_index("ix_point_transactions_source", table_name="point_transactions")
    op.drop_index(op.f("ix_point_transactions_created_at"), table_name="point_transactions")
    op.drop_index(op.f("ix_point_transactions_source_type"), table_name="point_transactions")
    op.drop_index(op.f("ix_point_transactions_transaction_type"), table_name="point_transactions")
    op.drop_index(op.f("ix_point_transactions_user_id"), table_name="point_transactions")
    op.drop_table("point_transactions")

    op.drop_index(op.f("ix_point_rules_is_active"), table_name="point_rules")
    op.drop_index(op.f("ix_point_rules_action_type"), table_name="point_rules")
    op.drop_table("point_rules")
