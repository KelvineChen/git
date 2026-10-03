from datetime import datetime

from sqlalchemy import Boolean, JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
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
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    admin_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(30), default="user", nullable=False)
    admin_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    profile: Mapped["UserProfile | None"] = relationship(back_populates="user")
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    match_records: Mapped[list["MatchRecord"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


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
    contact_method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    contact_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_visible: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
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
    moderation_status: Mapped[str] = mapped_column(
        String(30), default="active", nullable=False
    )
    moderation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    moderation_previous_status: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
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
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_match_record"),
    )

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


class OwnerInterest(Base):
    __tablename__ = "owner_interests"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_owner_interest"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="interested", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_project_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="notifications")


class FavoriteProject(Base):
    __tablename__ = "favorite_projects"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_favorite_project"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_page: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    admin_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
