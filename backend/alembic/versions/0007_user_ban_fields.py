"""Add user account ban fields.

Revision ID: 0007_user_ban_fields
Revises: 0006_project_moderation
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_user_ban_fields"
down_revision = "0006_project_moderation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_banned" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "is_banned",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    if "banned_at" not in columns:
        op.add_column("users", sa.Column("banned_at", sa.DateTime(), nullable=True))
    if "ban_reason" not in columns:
        op.add_column(
            "users",
            sa.Column("ban_reason", sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    for name in ("ban_reason", "banned_at", "is_banned"):
        if name in columns:
            op.drop_column("users", name)
