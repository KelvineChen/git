from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BACKEND_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
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


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
