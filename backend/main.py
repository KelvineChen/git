import re

from fastapi import FastAPI
from pydantic import BaseModel

from ai_service import (
    judge_experience_relevance,
    judge_skill_similarity,
    normalize_skills,
    parse_project_requirement,
    parse_user_profile,
)

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
