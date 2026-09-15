import re

from fastapi import FastAPI
from pydantic import BaseModel

from ai_service import parse_project_requirement, parse_user_profile

app = FastAPI()

@app.get("/")
def root():
    return {"message": "欢迎来到知遇Link API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

class ProfileRequest(BaseModel):
    raw_text: str


class MatchRequest(BaseModel):
    user_profile: dict
    project_profile: dict

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


def _hours(value: str) -> float:
    """Extract the first hour value from text such as '8小时/周'."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:小时|h)", value or "", re.IGNORECASE)
    return float(match.group(1)) if match else 0


def _keywords(text: str) -> set[str]:
    return {
        item.lower()
        for item in re.findall(r"[A-Za-z0-9+#.]+|[\u4e00-\u9fff]{2,}", text or "")
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

    required_skills = project["required_skills"]
    user_skills = {str(skill).lower() for skill in user["skills"]}
    required_skill_names = {str(skill).lower() for skill in required_skills}
    skill_match = (
        len(user_skills & required_skill_names) / len(required_skill_names)
        if required_skill_names else 0
    )

    time_match = int(_hours(str(user["time_commitment"])) >= _hours(str(project["time_requirement"])))
    project_keywords = _keywords(str(project["project_type"]))
    experience_keywords = _keywords(" ".join(map(str, user["experience"])))
    experience_match = int(bool(project_keywords & experience_keywords))

    total_score = skill_match * 0.6 + time_match * 0.2 + experience_match * 0.2
    skill_text = "良好" if skill_match >= 0.5 else "不足"
    experience_text = "相关" if experience_match else "相关性不足"
    time_text = "充足" if time_match else "不足"
    explanation = (
        f"技能匹配{skill_text}，经验{experience_text}，时间投入{time_text}"
    )

    return {
        "success": True,
        "total_score": round(total_score, 3),
        "skill_match": round(skill_match, 3),
        "time_match": time_match,
        "experience_match": experience_match,
        "explanation": explanation,
    }
