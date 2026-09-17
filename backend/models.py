from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
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
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
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
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
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
