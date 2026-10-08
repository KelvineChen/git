"""Add persisted user sessions and email verification.

Revision ID: 0008_email_verification
Revises: 0007_user_ban_fields
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_email_verification"
down_revision = "0007_user_ban_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "email_verified_at" not in user_columns:
        op.add_column(
            "users",
            sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        )
    table_names = set(inspector.get_table_names())
    if "user_sessions" not in table_names:
        op.create_table(
            "user_sessions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("token_hash"),
        )
        op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
        op.create_index("ix_user_sessions_token_hash", "user_sessions", ["token_hash"])
        op.create_index("ix_user_sessions_expires_at", "user_sessions", ["expires_at"])

    if "email_verifications" not in table_names:
        op.create_table(
            "email_verifications",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("code_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("consumed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_email_verifications_user_id", "email_verifications", ["user_id"]
        )
        op.create_index(
            "ix_email_verifications_email", "email_verifications", ["email"]
        )
        op.create_index(
            "ix_email_verifications_expires_at",
            "email_verifications",
            ["expires_at"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    table_names = set(inspector.get_table_names())
    if "email_verifications" in table_names:
        op.drop_table("email_verifications")
    if "user_sessions" in table_names:
        op.drop_table("user_sessions")
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "email_verified_at" in user_columns:
        op.drop_column("users", "email_verified_at")
