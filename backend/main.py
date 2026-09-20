import hashlib
import re
import secrets
from uuid import uuid4

import bcrypt
import models

from fastapi import Depends, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_service import (
    judge_experience_relevance,
    judge_skill_similarity,
    normalize_skills,
    parse_project_requirement,
    parse_user_profile,
)
from database import Base, engine, get_db, init_db
from models import (
    MatchRecord,
    OwnerInterest,
    Project,
    ProjectProfile,
    User,
    UserProfile,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()
ADMIN_TOKENS: set[str] = set()


@app.on_event("startup")
def startup_event() -> None:
    init_db()

@app.get("/")
def root():
    return {"message": "欢迎来到知遇Link API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

class ProfileRequest(BaseModel):
    raw_text: str


class AuthRegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str
    school: str
    major: str
    grade: str


class AuthLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginRequest(BaseModel):
    admin_name: str
    admin_password: str
    user_password: str


class AdminRegisterRequest(BaseModel):
    admin_name: str
    admin_password: str
    confirm_admin_password: str
    user_password: str


class AdminReviewActionRequest(BaseModel):
    admin_name: str
    action: str


class MatchRequest(BaseModel):
    user_profile: dict
    project_profile: dict


class SaveProfileRequest(BaseModel):
    user_id: int
    raw_text: str
    parsed_data: dict


class CreateProjectRequest(BaseModel):
    owner_id: int
    name: str
    raw_text: str
    parsed_data: dict
    scope: str = "same_school"


class InterestRequest(BaseModel):
    user_id: int
    project_id: int


class ProjectStatusRequest(BaseModel):
    owner_id: int
    project_id: int
    status: str


def _hash_password(password: str) -> str:
    """Hash a password with a per-user salt for database storage."""
    iterations = 600_000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a password against the stored PBKDF2 hash."""
    if not password_hash:
        return False

    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_text)
        expected_digest = bytes.fromhex(digest_text)
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return secrets.compare_digest(actual_digest, expected_digest)
    except (TypeError, ValueError):
        return False


def _verify_bcrypt_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


@app.post("/api/auth/register")
def auth_register(
    request: AuthRegisterRequest,
    db: Session = Depends(get_db),
):
    username = request.username.strip()
    email = request.email.strip()
    school = request.school.strip()
    major = request.major.strip()
    grade = request.grade.strip()

    if request.password != request.confirm_password:
        return JSONResponse(
            status_code=400,
            content={"error": "password_mismatch"},
        )

    if len(request.password) < 8:
        return JSONResponse(
            status_code=400,
            content={"error": "password_too_short"},
        )

    if not username or not email or not request.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_input"},
        )

    existing_username = db.scalar(
        select(User).where(User.username == username)
    )
    if existing_username:
        return JSONResponse(
            status_code=400,
            content={"error": "username_taken"},
        )

    existing_email = db.scalar(select(User).where(User.email == email))
    if existing_email:
        return JSONResponse(
            status_code=400,
            content={"error": "email_taken"},
        )

    user = User(
        username=username,
        email=email,
        password_hash=_hash_password(request.password),
        school=school,
        major=major,
        grade=grade,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"error": "registration_failed"},
        )
    except SQLAlchemyError:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": "registration_failed"},
        )

    return {"status": "ok"}


@app.post("/api/admin/register")
def admin_register(
    request: AdminRegisterRequest,
    db: Session = Depends(get_db),
):
    admin_name = request.admin_name.strip()
    if not admin_name or len(admin_name) > 100:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_admin_name"},
        )
    if request.admin_password != request.confirm_admin_password:
        return JSONResponse(
            status_code=400,
            content={"error": "password_mismatch"},
        )
    if len(request.admin_password) < 8 or len(request.user_password) < 8:
        return JSONResponse(
            status_code=400,
            content={"error": "password_too_short"},
        )

    existing = db.scalar(
        select(User).where(
            (User.admin_name == admin_name) | (User.username == admin_name)
        )
    )
    if existing:
        return JSONResponse(
            status_code=400,
            content={"error": "admin_name_exists"},
        )

    admin = User(
        admin_name=admin_name,
        username=admin_name,
        email=f"admin-{uuid4().hex}@local.invalid",
        admin_password_hash=bcrypt.hashpw(
            request.admin_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8"),
        user_password_hash=bcrypt.hashpw(
            request.user_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8"),
        role="admin",
        admin_status="pending",
    )
    try:
        db.add(admin)
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"error": "admin_name_exists"},
        )
    except SQLAlchemyError:
        db.rollback()
        return _server_error()
    return {"status": "ok", "admin_status": "pending"}


@app.post("/api/auth/login")
def auth_login(
    request: AuthLoginRequest,
    db: Session = Depends(get_db),
):
    username = request.username.strip()

    user = db.scalar(select(User).where(User.username == username))
    if not user:
        return JSONResponse(
            status_code=400,
            content={"error": "user_not_found"},
        )

    if not _verify_password(request.password, user.password_hash):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_password"},
        )

    token = str(uuid4())
    return {
        "status": "ok",
        "token": token,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "school": user.school,
    }


@app.post("/api/admin/login")
def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    admin_name = request.admin_name.strip()
    admin = db.scalar(
        select(User).where(
            (User.admin_name == admin_name) | (User.username == admin_name)
        )
    )
    if not admin or admin.role != "admin":
        return JSONResponse(
            status_code=400,
            content={"error": "admin_not_found"},
        )

    if not _verify_bcrypt_password(
        request.admin_password,
        admin.admin_password_hash,
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_admin_password"},
        )

    if not _verify_bcrypt_password(
        request.user_password,
        admin.user_password_hash,
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_user_password"},
        )

    if admin.admin_status != "approved":
        return JSONResponse(
            status_code=400,
            content={"error": "admin_not_approved"},
        )

    token = str(uuid4())
    ADMIN_TOKENS.add(token)
    return {
        "status": "ok",
        "token": token,
        "admin_name": admin.admin_name or admin.username,
        "admin_status": admin.admin_status,
    }


def _require_admin_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return "admin_token_required"

    token = authorization.removeprefix("Bearer ").strip()
    if token not in ADMIN_TOKENS:
        return "invalid_admin_token"

    return None


def _admin_auth_response(authorization: str | None) -> JSONResponse | None:
    error = _require_admin_token(authorization)
    if error:
        return JSONResponse(status_code=401, content={"error": error})
    return None


def _server_error() -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "server_error"})


def _serialize_user(user: User) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "school": user.school,
        "major": user.major,
        "grade": user.grade,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
    }


@app.get("/api/admin/users")
def admin_users(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        users = db.scalars(select(User).order_by(User.created_at.desc())).all()
        return [_serialize_user(user) for user in users]
    except Exception:
        return _server_error()


@app.get("/api/admin/users/search")
def admin_users_search(
    username: str = "",
    school: str = "",
    major: str = "",
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        conditions = []
        if username.strip():
            conditions.append(User.username.ilike(f"%{username.strip()}%"))
        if school.strip():
            conditions.append(User.school.ilike(f"%{school.strip()}%"))
        if major.strip():
            conditions.append(User.major.ilike(f"%{major.strip()}%"))

        statement = select(User).order_by(User.created_at.desc())
        if conditions:
            statement = statement.where(*conditions)
        users = db.scalars(statement).all()
        return [_serialize_user(user) for user in users]
    except Exception:
        return _server_error()


def _serialize_competition(project: Project) -> dict:
    return {
        "id": project.id,
        "title": project.name,
        "creator": project.owner.username if project.owner else "",
        "description": project.raw_text or "",
        "created_at": project.created_at.isoformat(),
    }


@app.get("/api/admin/competitions")
def admin_competitions(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        projects = db.scalars(
            select(Project).order_by(Project.created_at.desc())
        ).all()
        return [_serialize_competition(project) for project in projects]
    except Exception:
        return _server_error()


@app.get("/api/admin/competitions/search")
def admin_competitions_search(
    title: str = "",
    creator: str = "",
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        statement = (
            select(Project)
            .join(User, Project.owner_id == User.id)
            .order_by(Project.created_at.desc())
        )
        if title.strip():
            statement = statement.where(
                Project.name.ilike(f"%{title.strip()}%")
            )
        if creator.strip():
            statement = statement.where(
                User.username.ilike(f"%{creator.strip()}%")
            )

        projects = db.scalars(statement).all()
        return [_serialize_competition(project) for project in projects]
    except Exception:
        return _server_error()


@app.get("/api/admin/review/list")
def admin_review_list(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        statement = (
            select(User)
            .where(
                User.role == "admin",
                User.admin_status == "pending",
            )
            .order_by(User.created_at.asc())
        )
        admins = db.scalars(statement).all()
        return [
            {
                "admin_name": admin.admin_name or admin.username,
                "username": admin.username,
                "created_at": admin.created_at.isoformat(),
                "admin_status": admin.admin_status,
            }
            for admin in admins
        ]
    except Exception:
        return _server_error()


@app.post("/api/admin/review/action")
def admin_review_action(
    request: AdminReviewActionRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    action = request.action.strip().lower()
    if action not in {"approve", "reject"}:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_action"},
        )

    try:
        admin = db.scalar(
            select(User).where(
                User.role == "admin",
                (User.admin_name == request.admin_name.strip())
                | (User.username == request.admin_name.strip()),
            )
        )
        if not admin:
            return JSONResponse(
                status_code=404,
                content={"error": "admin_not_found"},
            )

        admin.admin_status = "approved" if action == "approve" else "rejected"
        db.commit()
        return {
            "status": "ok",
            "admin_name": admin.admin_name or admin.username,
            "admin_status": admin.admin_status,
        }
    except Exception:
        db.rollback()
        return _server_error()


@app.get("/api/admin/user/{username}")
def admin_user_detail(
    username: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        user = db.scalar(select(User).where(User.username == username))
        if not user:
            return JSONResponse(
                status_code=404,
                content={"error": "user_not_found"},
            )
        return _serialize_user(user)
    except Exception:
        return _server_error()


@app.get("/api/admin/competition/{competition_id}")
def admin_competition_detail(
    competition_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    auth_error = _admin_auth_response(authorization)
    if auth_error:
        return auth_error

    try:
        project = db.get(Project, competition_id)
        if not project:
            return JSONResponse(
                status_code=404,
                content={"error": "competition_not_found"},
            )
        return _serialize_competition(project)
    except Exception:
        return _server_error()


@app.post("/api/save_profile")
def save_profile(request: SaveProfileRequest, db: Session = Depends(get_db)):
    if db.get(User, request.user_id) is None:
        return {"success": False, "message": "用户不存在"}

    profile = db.scalar(
        select(UserProfile).where(UserProfile.user_id == request.user_id)
    )
    data = request.parsed_data
    values = {
        "raw_text": request.raw_text,
        "skills": data.get("skills", []),
        "skill_levels": data.get("skill_levels", {}),
        "experience": data.get("experience", []),
        "interests": data.get("interests", []),
        "preference": data.get("preference", ""),
        "time_commitment": data.get("time_commitment", "未知"),
    }

    if profile:
        for field, value in values.items():
            setattr(profile, field, value)
    else:
        profile = UserProfile(user_id=request.user_id, **values)
        db.add(profile)

    try:
        db.execute(
            delete(MatchRecord).where(MatchRecord.user_id == request.user_id)
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "画像保存失败"}

    return {"success": True}


@app.post("/api/create_project")
def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    if db.get(User, request.owner_id) is None:
        return {"success": False, "message": "用户不存在"}

    data = request.parsed_data
    project = Project(
        owner_id=request.owner_id,
        name=request.name,
        raw_text=request.raw_text,
        scope=request.scope,
    )

    try:
        db.add(project)
        db.flush()
        db.add(
            ProjectProfile(
                project_id=project.id,
                required_skills=data.get("required_skills", []),
                time_requirement=data.get("time_requirement", "未知"),
                priority=data.get("priority", []),
                project_type=data.get("project_type", ""),
                background=data.get("background", ""),
            )
        )
        db.commit()
        db.refresh(project)
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "项目创建失败"}

    return {"success": True, "project_id": project.id}


@app.post("/api/project_status")
def update_project_status(
    request: ProjectStatusRequest,
    db: Session = Depends(get_db),
):
    project = db.get(Project, request.project_id)
    if not project:
        return {"success": False, "message": "项目不存在"}
    if project.owner_id != request.owner_id:
        return {"success": False, "message": "无权修改该项目"}

    allowed_statuses = {"recruiting", "full", "closed", "completed"}
    if request.status not in allowed_statuses:
        return {"success": False, "message": "项目状态无效"}

    project.status = request.status
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "项目状态更新失败"}
    return {"success": True, "status": project.status}


@app.delete("/api/project/{project_id}")
def delete_project(
    project_id: int,
    owner_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        return {"success": False, "message": "项目不存在"}
    if project.owner_id != owner_id:
        return {"success": False, "message": "无权删除该项目"}

    try:
        db.execute(
            delete(OwnerInterest).where(OwnerInterest.project_id == project_id)
        )
        db.execute(
            delete(MatchRecord).where(MatchRecord.project_id == project_id)
        )
        db.execute(
            delete(ProjectProfile).where(ProjectProfile.project_id == project_id)
        )
        db.delete(project)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "项目删除失败"}
    return {"success": True}


@app.get("/api/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if not profile:
        return {"success": False, "message": "画像不存在"}

    return {
        "success": True,
        "user_id": profile.user_id,
        "raw_text": profile.raw_text,
        "skills": profile.skills,
        "skill_levels": profile.skill_levels,
        "experience": profile.experience,
        "interests": profile.interests,
        "preference": profile.preference,
        "time_commitment": profile.time_commitment,
        "updated_at": profile.updated_at,
    }


@app.get("/api/project/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        return {"success": False, "message": "项目不存在"}

    profile = db.scalar(
        select(ProjectProfile).where(ProjectProfile.project_id == project_id)
    )
    return {
        "success": True,
        "project_id": project.id,
        "owner_id": project.owner_id,
        "name": project.name,
        "raw_text": project.raw_text,
        "status": project.status,
        "scope": project.scope,
        "created_at": project.created_at,
        "required_skills": profile.required_skills if profile else [],
        "time_requirement": profile.time_requirement if profile else "未知",
        "priority": profile.priority if profile else [],
        "project_type": profile.project_type if profile else "",
        "background": profile.background if profile else "",
        "updated_at": profile.updated_at if profile else None,
    }


@app.get("/api/my_projects/{user_id}")
def get_my_projects(user_id: int, db: Session = Depends(get_db)):
    if db.get(User, user_id) is None:
        return {"success": False, "message": "用户不存在"}

    rows = db.execute(
        select(Project, ProjectProfile)
        .outerjoin(ProjectProfile, ProjectProfile.project_id == Project.id)
        .where(Project.owner_id == user_id)
        .order_by(Project.created_at.desc(), Project.id.desc())
    ).all()

    projects = []
    for project, profile in rows:
        projects.append(
            {
                "project_id": project.id,
                "name": project.name,
                "status": project.status,
                "scope": project.scope,
                "created_at": project.created_at.date().isoformat(),
                "raw_text": project.raw_text or "",
                "required_skills": profile.required_skills if profile else [],
                "time_requirement": (
                    profile.time_requirement if profile else "未知"
                ),
                "priority": profile.priority if profile else [],
                "project_type": profile.project_type if profile else "",
                "background": profile.background if profile else "",
            }
        )

    return {"success": True, "projects": projects}


@app.post("/api/interest")
def mark_interest(request: InterestRequest, db: Session = Depends(get_db)):
    if db.get(User, request.user_id) is None:
        return {"success": False, "message": "用户不存在"}
    if db.get(Project, request.project_id) is None:
        return {"success": False, "message": "项目不存在"}

    records = db.scalars(
        select(MatchRecord)
        .where(
            MatchRecord.user_id == request.user_id,
            MatchRecord.project_id == request.project_id,
        )
    ).all()
    if records:
        for record in records:
            record.status = "interested"
    else:
        db.add(
            MatchRecord(
                user_id=request.user_id,
                project_id=request.project_id,
                total_score=0.0,
                skill_match=0.0,
                time_match=0.0,
                experience_match=0.0,
                explanation="尚未计算匹配度",
                status="interested",
            )
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concurrent_record = db.scalar(
            select(MatchRecord).where(
                MatchRecord.user_id == request.user_id,
                MatchRecord.project_id == request.project_id,
            )
        )
        if concurrent_record is None:
            return {"success": False, "message": "感兴趣状态保存失败"}
        concurrent_record.status = "interested"
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            return {"success": False, "message": "感兴趣状态保存失败"}
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "感兴趣状态保存失败"}
    return {
        "success": True,
        "status": "interested",
        "interested": True,
    }


@app.get("/api/interested_users/{project_id}")
def get_interested_users(project_id: int, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        return {"success": False, "message": "项目不存在"}

    rows = db.execute(
        select(User, MatchRecord)
        .join(MatchRecord, MatchRecord.user_id == User.id)
        .where(
            MatchRecord.project_id == project_id,
            MatchRecord.status == "interested",
        )
        .order_by(MatchRecord.total_score.desc())
    ).all()

    users_by_id = {}
    for user, record in rows:
        current = users_by_id.get(user.id)
        if current is None or record.total_score > current["total_score"]:
            users_by_id[user.id] = {
                "user_id": user.id,
                "username": user.username,
                "school": user.school or "",
                "total_score": round(record.total_score, 3),
            }
    users = sorted(
        users_by_id.values(),
        key=lambda item: item["total_score"],
        reverse=True,
    )
    return {"success": True, "users": users}


@app.post("/api/owner_interest")
def mark_owner_interest(request: InterestRequest, db: Session = Depends(get_db)):
    project = db.get(Project, request.project_id)
    if not project:
        return {"success": False, "message": "项目不存在"}
    if db.get(User, request.user_id) is None:
        return {"success": False, "message": "用户不存在"}
    if project.owner_id == request.user_id:
        return {"success": False, "message": "不能标记项目发起人本人"}

    existing = db.scalar(
        select(OwnerInterest).where(
            OwnerInterest.project_id == request.project_id,
            OwnerInterest.user_id == request.user_id,
        )
    )
    if existing is None:
        db.add(
            OwnerInterest(
                project_id=request.project_id,
                user_id=request.user_id,
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return {"success": False, "message": "发起人意向保存失败"}
    return {"success": True}


@app.post("/api/check_mutual")
def check_mutual(request: InterestRequest, db: Session = Depends(get_db)):
    user_interested = db.scalar(
        select(MatchRecord.id)
        .where(
            MatchRecord.user_id == request.user_id,
            MatchRecord.project_id == request.project_id,
            MatchRecord.status == "interested",
        )
        .limit(1)
    )
    owner_interested = db.scalar(
        select(OwnerInterest.id)
        .where(
            OwnerInterest.project_id == request.project_id,
            OwnerInterest.user_id == request.user_id,
        )
        .limit(1)
    )
    return {"mutual": bool(user_interested and owner_interested)}

@app.post("/api/parse_profile")
def parse_profile(request: ProfileRequest):
    try:
        result = parse_user_profile(request.raw_text)
        return {"success": True, "data": result}
    except Exception:
        return {"success": False, "message": "解析失败，请重试"}


@app.post("/api/parse_project")
def parse_project(request: ProfileRequest):
    try:
        result = parse_project_requirement(request.raw_text)
        return {"success": True, "data": result}
    except Exception:
        return {"success": False, "message": "解析失败，请重试"}


def _hours(value: str) -> float | None:
    """Extract hours from Chinese or English weekly time descriptions."""
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:小时|hours?|hrs?|h)",
        value or "",
        re.IGNORECASE,
    )
    return float(match.group(1)) if match else None


def _calculate_time_match(user_time: str, project_time: str) -> float:
    user_hours = _hours(user_time)
    project_hours = _hours(project_time)

    print("[match debug] extracted user hours:", user_hours)
    print("[match debug] extracted project hours:", project_hours)

    if user_hours is None or project_hours is None or project_hours <= 0:
        return 0.5
    if user_hours >= project_hours:
        return 1.0
    if user_hours >= project_hours * 0.8:
        return 0.7
    if user_hours >= project_hours * 0.5:
        return 0.4
    return 0.1


def _display_list(values: list) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return "、".join(cleaned) if cleaned else "未提供"


def _build_match_explanation(
    total_score: float,
    skill_match: float,
    time_match: float,
    experience_match: float,
    user_skills: list[str],
    required_skills: list[str],
    user_time: str,
    project_time: str,
    user_experience: list[str],
    project_type: str,
) -> str:
    if total_score >= 0.8:
        overall = "整体高度匹配。"
    elif total_score >= 0.5:
        overall = "整体部分匹配。"
    else:
        overall = "整体匹配度较低。"

    advantages = []
    gaps = []

    if skill_match >= 0.7:
        advantages.append(
            f"技能匹配度较高（{skill_match:.0%}），你的技能为"
            f"{_display_list(user_skills)}，项目需要{_display_list(required_skills)}。"
        )
    elif skill_match < 0.5:
        gaps.append(
            f"技能维度与项目需求重合度不足（{skill_match:.0%}）：项目需要"
            f"{_display_list(required_skills)}，你的技能为{_display_list(user_skills)}。"
        )
    else:
        gaps.append(
            f"技能仅部分覆盖（{skill_match:.0%}）：项目需要"
            f"{_display_list(required_skills)}，你的技能为{_display_list(user_skills)}。"
        )

    if time_match >= 0.7:
        advantages.append(
            f"时间投入满足度较高（用户可投入{user_time}，项目要求{project_time}）。"
        )
    elif time_match < 0.5:
        gaps.append(
            f"时间投入不足（用户可投入{user_time}，项目要求{project_time}）。"
        )
    else:
        gaps.append(
            f"时间信息不足，暂按中性分处理（用户时间：{user_time}；"
            f"项目时间：{project_time}）。"
        )

    if experience_match >= 0.7:
        advantages.append(
            f"经验方向与项目较相关（用户经历：{_display_list(user_experience)}；"
            f"项目类型：{project_type or '未提供'}）。"
        )
    elif experience_match < 0.5:
        gaps.append(
            f"经验方向与项目相关性较低（用户经历：{_display_list(user_experience)}；"
            f"项目类型：{project_type or '未提供'}）。"
        )
    else:
        gaps.append(
            f"经验相关性尚不明确（用户经历：{_display_list(user_experience)}；"
            f"项目类型：{project_type or '未提供'}）。"
        )

    advantage_text = "具体优势：" + "".join(advantages) if advantages else "具体优势：暂未发现明显高分维度。"
    gap_text = "具体差距：" + "".join(gaps) if gaps else "具体差距：暂未发现明显短板。"
    return overall + advantage_text + gap_text


def _calculate_match_scores(
    user: dict,
    project: dict,
    experience_score: float | None = None,
) -> dict:
    """Calculate all matching dimensions for one user/project pair."""
    normalized_user_skills = normalize_skills(user["skills"])
    normalized_user_interests = normalize_skills(user.get("interests", []))
    normalized_required_skills = normalize_skills(project["required_skills"])
    user_skills = {skill.lower() for skill in normalized_user_skills}
    user_interests = {interest.lower() for interest in normalized_user_interests}
    required_skill_names = {
        skill.lower() for skill in normalized_required_skills
    }

    print("[match debug] normalized user skills:", normalized_user_skills)
    print("[match debug] normalized user interests:", normalized_user_interests)
    print("[match debug] normalized required skills:", normalized_required_skills)

    skill_similarity_results = judge_skill_similarity(
        normalized_user_skills,
        normalized_required_skills,
    )
    skill_hit_count = sum(
        1 for _, _, similarity in skill_similarity_results if similarity >= 0.7
    )
    if not skill_similarity_results:
        skill_hit_count = len(user_skills & required_skill_names)

    interest_similarity_results = judge_skill_similarity(
        normalized_user_interests,
        normalized_required_skills,
    )
    interest_hit_count = sum(
        1 for _, _, similarity in interest_similarity_results if similarity >= 0.7
    )
    if not interest_similarity_results:
        interest_hit_count = len(user_interests & required_skill_names)

    skill_match = (
        min(
            (skill_hit_count + 0.5 * interest_hit_count)
            / len(required_skill_names),
            1.0,
        )
        if required_skill_names
        else 0
    )

    print("[match debug] skill similarity results:", skill_similarity_results)
    print("[match debug] interest similarity results:", interest_similarity_results)
    print("[match debug] skill hit count:", skill_hit_count)
    print("[match debug] interest hit count:", interest_hit_count)

    time_match = _calculate_time_match(
        str(user["time_commitment"]),
        str(project["time_requirement"]),
    )
    print("[match debug] time match score:", time_match)
    project_type = str(project["project_type"])
    project_background = str(project.get("background", ""))
    experience_match = (
        experience_score
        if experience_score is not None
        else judge_experience_relevance(
            user_experience=user["experience"],
            project_type=project_type,
            project_background=project_background,
        )
    )

    print("[match debug] user experience:", user["experience"])
    print("[match debug] project type:", project_type)
    print("[match debug] project background:", project_background)
    print("[match debug] AI experience score:", experience_match)

    total_score = skill_match * 0.6 + time_match * 0.2 + experience_match * 0.2
    explanation = _build_match_explanation(
        total_score=total_score,
        skill_match=skill_match,
        time_match=time_match,
        experience_match=experience_match,
        user_skills=normalized_user_skills,
        required_skills=normalized_required_skills,
        user_time=str(user["time_commitment"]),
        project_time=str(project["time_requirement"]),
        user_experience=user["experience"],
        project_type=project_type,
    )

    return {
        "total_score": round(total_score, 3),
        "skill_match": round(skill_match, 3),
        "time_match": time_match,
        "experience_match": experience_match,
        "explanation": explanation,
    }


@app.post("/api/match")
def match_profiles(request: MatchRequest):
    user = request.user_profile
    project = request.project_profile

    required_fields = {
        "user": (user, ["skills", "skill_levels", "time_commitment", "experience"]),
        "project": (project, ["required_skills", "time_requirement", "project_type"]),
    }
    if any(field not in data for data, fields in required_fields.values() for field in fields):
        return {"success": False, "message": "数据不完整"}

    return {"success": True, **_calculate_match_scores(user, project)}


@app.get("/api/match_list/{user_id}")
def get_match_list(
    user_id: int,
    scope: str | None = None,
    db: Session = Depends(get_db),
):
    user_profile = db.scalar(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    if not user_profile:
        return {"success": False, "message": "请先填写画像"}

    current_user = db.get(User, user_id)
    if not current_user:
        return {"success": False, "message": "用户不存在"}

    query = (
        select(Project, ProjectProfile, User)
        .join(ProjectProfile, ProjectProfile.project_id == Project.id)
        .join(User, User.id == Project.owner_id)
        .where(Project.status == "recruiting")
    )
    if scope == "same_school":
        if not current_user.school:
            return {"success": True, "matches": []}
        query = query.where(User.school == current_user.school)

    user_data = {
        "skills": user_profile.skills or [],
        "skill_levels": user_profile.skill_levels or {},
        "experience": user_profile.experience or [],
        "interests": user_profile.interests or [],
        "time_commitment": user_profile.time_commitment or "未知",
    }
    matches = []
    experience_cache: dict[tuple[int, int], float] = {}

    try:
        for project, project_profile, owner in db.execute(query).all():
            project_data = {
                "required_skills": project_profile.required_skills or [],
                "time_requirement": project_profile.time_requirement or "未知",
                "project_type": project_profile.project_type or "",
                "background": project_profile.background or "",
            }
            cache_key = (user_id, project.id)
            record = db.scalars(
                select(MatchRecord)
                .where(
                    MatchRecord.user_id == user_id,
                    MatchRecord.project_id == project.id,
                )
                .limit(1)
            ).first()
            if cache_key not in experience_cache:
                experience_cache[cache_key] = (
                    record.experience_match
                    if record is not None
                    and record.explanation != "尚未计算匹配度"
                    else judge_experience_relevance(
                        user_experience=user_data["experience"],
                        project_type=project_data["project_type"],
                        project_background=project_data["background"],
                    )
                )

            scores = _calculate_match_scores(
                user_data,
                project_data,
                experience_score=experience_cache[cache_key],
            )
            if record is None:
                record = MatchRecord(user_id=user_id, project_id=project.id, **scores)
                db.add(record)
            else:
                for field in (
                    "total_score",
                    "skill_match",
                    "time_match",
                    "experience_match",
                    "explanation",
                ):
                    setattr(record, field, scores[field])

            matches.append(
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "owner_school": owner.school or "",
                    **scores,
                    "scope": project.scope,
                    "status": record.status or "pending",
                    "interested": record.status == "interested",
                }
            )

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return {"success": False, "message": "匹配结果保存失败"}

    matches.sort(key=lambda item: item["total_score"], reverse=True)
    return {"success": True, "matches": matches}
