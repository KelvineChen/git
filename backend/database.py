from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "zhilink.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_name: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    admin_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(30), default="user", nullable=False)
    admin_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    school: Mapped[str | None] = mapped_column(String, nullable=True)
    major: Mapped[str | None] = mapped_column(String, nullable=True)
    grade: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    profile: Mapped["UserProfile | None"] = relationship(back_populates="user")
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    match_records: Mapped[list["MatchRecord"]] = relationship(back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    skill_levels: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    experience: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    interests: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preference: Mapped[str | None] = mapped_column(String, nullable=True)
    time_commitment: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="profile")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="recruiting", nullable=False)
    scope: Mapped[str] = mapped_column(String, default="same_school", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    owner: Mapped[User] = relationship(back_populates="projects")
    profile: Mapped["ProjectProfile | None"] = relationship(back_populates="project")
    match_records: Mapped[list["MatchRecord"]] = relationship(back_populates="project")


class ProjectProfile(Base):
    __tablename__ = "project_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    required_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    time_requirement: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    project_type: Mapped[str | None] = mapped_column(String, nullable=True)
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="profile")


class MatchRecord(Base):
    __tablename__ = "match_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_match: Mapped[float] = mapped_column(Float, nullable=False)
    time_match: Mapped[float] = mapped_column(Float, nullable=False)
    experience_match: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    user: Mapped[User] = relationship(back_populates="match_records")
    project: Mapped[Project] = relationship(back_populates="match_records")


def init_db() -> None:
    """Create the data directory and all database tables if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

    # Keep existing SQLite databases compatible after adding auth fields.
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
    """Yield a request-scoped database session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
