"""Add project favorites and user feedback.

Revision ID: 0005_favorites_feedback
Revises: 0004_notifications
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_favorites_feedback"
down_revision = "0004_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "favorite_projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "project_id", name="uq_favorite_project"),
    )
    op.create_index("ix_favorite_projects_user_id", "favorite_projects", ["user_id"])
    op.create_index("ix_favorite_projects_project_id", "favorite_projects", ["project_id"])

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("source_page", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("admin_reply", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_category", "feedback", ["category"])
    op.create_index("ix_feedback_status", "feedback", ["status"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("favorite_projects")
