"""Add candidate decision status to owner interests.

Revision ID: 0002_owner_interest_status
Revises: 0001_initial_schema
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_owner_interest_status"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "owner_interests",
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="interested",
        ),
    )


def downgrade() -> None:
    op.drop_column("owner_interests", "status")
