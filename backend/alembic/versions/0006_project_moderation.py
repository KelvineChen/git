"""Add project moderation fields.

Revision ID: 0006_project_moderation
Revises: 0005_favorites_feedback
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_project_moderation"
down_revision = "0005_favorites_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "moderation_status",
            sa.String(length=30),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column("projects", sa.Column("moderation_reason", sa.Text(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("moderation_previous_status", sa.String(length=30), nullable=True),
    )
    op.add_column("projects", sa.Column("moderated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "moderated_at")
    op.drop_column("projects", "moderation_previous_status")
    op.drop_column("projects", "moderation_reason")
    op.drop_column("projects", "moderation_status")
