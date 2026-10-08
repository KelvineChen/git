from pathlib import Path
from typing import Generator
import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BACKEND_DIR / "app.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH.as_posix()}",
)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


def init_db() -> None:
    """Create tables and add authentication columns to older SQLite databases."""
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
    migrations = {
        "password_hash": "VARCHAR(255)",
        "admin_name": "VARCHAR(100)",
        "admin_password_hash": "VARCHAR(255)",
        "user_password_hash": "VARCHAR(255)",
        "role": "VARCHAR(30) DEFAULT 'user'",
        "admin_status": "VARCHAR(30)",
        "is_banned": "BOOLEAN NOT NULL DEFAULT 0",
        "banned_at": "DATETIME",
        "ban_reason": "VARCHAR(255)",
        "email_verified_at": "DATETIME",
    }
    missing_columns = [
        (name, column_type)
        for name, column_type in migrations.items()
        if name not in user_columns
    ]
    if missing_columns:
        with engine.begin() as connection:
            for name, column_type in missing_columns:
                connection.execute(
                    text(f"ALTER TABLE users ADD COLUMN {name} {column_type}")
                )

    owner_interest_columns = {
        column["name"] for column in inspect(engine).get_columns("owner_interests")
    }
    if "status" not in owner_interest_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE owner_interests ADD COLUMN status "
                    "VARCHAR(30) NOT NULL DEFAULT 'interested'"
                )
            )

    profile_columns = {
        column["name"] for column in inspect(engine).get_columns("user_profiles")
    }
    profile_migrations = {
        "contact_method": "VARCHAR(30)",
        "contact_value": "VARCHAR(255)",
        "contact_visible": "BOOLEAN NOT NULL DEFAULT 0",
    }
    missing_profile_columns = [
        (name, column_type)
        for name, column_type in profile_migrations.items()
        if name not in profile_columns
    ]
    if missing_profile_columns:
        with engine.begin() as connection:
            for name, column_type in missing_profile_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE user_profiles ADD COLUMN {name} {column_type}"
                    )
                )

    project_columns = {
        column["name"] for column in inspect(engine).get_columns("projects")
    }
    project_migrations = {
        "moderation_status": "VARCHAR(30) NOT NULL DEFAULT 'active'",
        "moderation_reason": "TEXT",
        "moderation_previous_status": "VARCHAR(30)",
        "moderated_at": "DATETIME",
    }
    missing_project_columns = [
        (name, column_type)
        for name, column_type in project_migrations.items()
        if name not in project_columns
    ]
    if missing_project_columns:
        with engine.begin() as connection:
            for name, column_type in missing_project_columns:
                connection.execute(
                    text(f"ALTER TABLE projects ADD COLUMN {name} {column_type}")
                )


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
