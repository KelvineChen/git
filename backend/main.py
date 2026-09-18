import hashlib
import re
import secrets
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_service import (
    judge_experience_relevance,
    judge_skill_similarity,
    normalize_skills,
    parse_project_requirement,
    parse_user_profile,
)
from database import (
    Project,
    ProjectProfile,
    User,
    UserProfile,
    get_db,
    init_db,
)

app = FastAPI()


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


class MatchRequest(BaseModel):
    user_profile: dict
    project_profile: dict


class RegisterRequest(BaseModel):
    username: str
    email: str
    school: str = ""
    major: str = ""
    grade: str = ""


class LoginRequest(BaseModel):
    email: str


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


@app.post("/api/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.scalar(
        select(User).where(
            or_(User.username == request.username, User.email == request.email)
        )
    )
    if existing_user:
        return {"success": False, "message": "用户名或邮箱已存在"}

    user = User(
        username=request.username,
        email=request.email,
        school=request.school,
        major=request.major,
        grade=request.grade,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return {"success": False, "message": "用户名或邮箱已存在"}

    return {
        "success": True,
        "user_id": user.id,
        "username": user.username,
    }


@app.post("/api/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == request.email))
    if not user:
        return {"success": False, "message": "用户不存在"}

    return {
        "success": True,
        "user_id": user.id,
        "username": user.username,
        "school": user.school,
    }


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
    experience_match = judge_experience_relevance(
        user_experience=user["experience"],
        project_type=project_type,
        project_background=project_background,
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
        "success": True,
        "total_score": round(total_score, 3),
        "skill_match": round(skill_match, 3),
        "time_match": time_match,
        "experience_match": experience_match,
        "explanation": explanation,
    }
