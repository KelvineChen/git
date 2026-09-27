"""create initial application schema

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("school", sa.String(), nullable=True),
        sa.Column("major", sa.String(), nullable=True),
        sa.Column("grade", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("admin_name", sa.String(length=100), nullable=True),
        sa.Column("admin_password_hash", sa.String(length=255), nullable=True),
        sa.Column("user_password_hash", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=30), server_default="user", nullable=False),
        sa.Column("admin_status", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("skill_levels", sa.JSON(), nullable=False),
        sa.Column("experience", sa.JSON(), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("preference", sa.String(), nullable=True),
        sa.Column("time_commitment", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=False)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="recruiting"),
        sa.Column("scope", sa.String(), nullable=False, server_default="same_school"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"], unique=False)

    op.create_table(
        "project_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("time_requirement", sa.String(), nullable=True),
        sa.Column("priority", sa.JSON(), nullable=False),
        sa.Column("project_type", sa.String(), nullable=True),
        sa.Column("background", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_profiles_project_id", "project_profiles", ["project_id"], unique=False)

    op.create_table(
        "match_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("skill_match", sa.Float(), nullable=False),
        sa.Column("time_match", sa.Float(), nullable=False),
        sa.Column("experience_match", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "project_id", name="uq_match_record"),
    )
    op.create_index("ix_match_records_project_id", "match_records", ["project_id"], unique=False)
    op.create_index("ix_match_records_user_id", "match_records", ["user_id"], unique=False)

    op.create_table(
        "owner_interests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_owner_interest"),
    )
    op.create_index("ix_owner_interests_project_id", "owner_interests", ["project_id"], unique=False)
    op.create_index("ix_owner_interests_user_id", "owner_interests", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("owner_interests")
    op.drop_table("match_records")
    op.drop_table("project_profiles")
    op.drop_table("projects")
    op.drop_table("user_profiles")
    op.drop_table("users")
