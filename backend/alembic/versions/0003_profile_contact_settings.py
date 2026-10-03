"""Add optional contact settings to user profiles.

Revision ID: 0003_profile_contact_settings
Revises: 0002_owner_interest_status
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_profile_contact_settings"
down_revision = "0002_owner_interest_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("contact_method", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("contact_value", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "contact_visible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "contact_visible")
    op.drop_column("user_profiles", "contact_value")
    op.drop_column("user_profiles", "contact_method")
