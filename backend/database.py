from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
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
    """Import all models and create any missing tables."""
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
