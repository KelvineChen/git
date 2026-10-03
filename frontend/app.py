import json
import os
import re
from html import escape
from urllib.parse import urlencode

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            --ink: #16233b;
            --muted: #667085;
            --line: #e5eaf2;
            --blue: #2764e7;
            --blue-soft: #eef4ff;
            --teal: #0b8f83;
            --surface: #ffffff;
            --canvas: #f5f7fb;
        }

        .stApp { background: var(--canvas); color: var(--ink); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stWidgetLabel"] p {
            color: var(--ink);
        }
        [data-testid="stSidebar"] {
            background: #101a2e;
            border-right: 0;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 { color: #e8eefb !important; }
        [data-testid="stSidebar"] .stRadio label { color: #cbd5e8; }
        [data-testid="stSidebar"] .stRadio label:hover { color: #ffffff; }
        [data-testid="stSidebar"] button {
            color: #e8eefb !important;
            background: #17243d !important;
            border-color: #34435f !important;
        }
        .block-container { max-width: 1180px; padding-top: 2.5rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
        h1 { font-size: 2.25rem !important; line-height: 1.15 !important; }
        h2 { font-size: 1.45rem !important; }
        h3 { font-size: 1.1rem !important; }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1rem 1.1rem;
            box-shadow: 0 4px 16px rgba(22, 35, 59, 0.04);
        }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); }
        div[data-testid="stButton"] > button {
            border-radius: 9px;
            min-height: 2.55rem;
            font-weight: 600;
            color: var(--ink) !important;
            background: #ffffff !important;
            border-color: #cbd5e1 !important;
        }
        div[data-testid="stButton"] > button:hover {
            color: var(--blue) !important;
            border-color: var(--blue) !important;
        }
        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button {
            color: #ffffff !important;
            background: var(--blue) !important;
            border-color: var(--blue) !important;
        }
        div[data-testid="stButton"] > button[kind="primary"] p,
        div[data-testid="stFormSubmitButton"] > button p {
            color: #ffffff !important;
        }
        div[data-testid="stButton"] > button:disabled {
            color: #7a8699 !important;
            background: #e8edf5 !important;
            border-color: #d8dfeb !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-baseweb="select"] > div {
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
            background: #ffffff !important;
            border-color: #cbd5e1 !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="base-input"],
        [data-testid="stTextArea"] [data-baseweb="textarea"] {
            color: var(--ink) !important;
            background: #ffffff !important;
        }
        [data-testid="stTextInputRootElement"],
        [data-testid="stTextAreaRootElement"] {
            color: var(--ink) !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stTextAreaRootElement"]:focus-within {
            border-color: var(--blue) !important;
            box-shadow: 0 0 0 1px var(--blue) !important;
        }
        [data-testid="stTextInput"] svg,
        [data-testid="stTextArea"] svg {
            fill: var(--muted) !important;
            color: var(--muted) !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #98a2b3 !important;
            -webkit-text-fill-color: #98a2b3 !important;
        }
        [data-baseweb="tab-list"] {
            border-bottom-color: var(--line) !important;
        }
        [data-baseweb="tab"] p {
            color: var(--muted) !important;
        }
        [aria-selected="true"][data-baseweb="tab"] p {
            color: var(--blue) !important;
        }
        div[data-testid="stForm"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1.2rem;
        }
        [data-testid="stExpander"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
        }
        .zl-eyebrow {
            color: var(--blue);
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin-bottom: .6rem;
        }
        .zl-hero {
            background: linear-gradient(135deg, #16233b 0%, #213d69 100%);
            border-radius: 18px;
            padding: 2rem 2.2rem;
            margin-bottom: 1.4rem;
            color: #ffffff;
            box-shadow: 0 12px 30px rgba(22, 35, 59, .16);
        }
        .zl-hero h1 {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        .zl-hero p { margin: .45rem 0 0; color: #d7e1f2 !important; font-size: 1rem; }
        .zl-section { margin: 1.7rem 0 .75rem; }
        .zl-section-title { color: var(--ink); font-size: 1.15rem; font-weight: 700; }
        .zl-section-caption { color: var(--muted); font-size: .9rem; margin-top: .2rem; }
        .zl-pill {
            display: inline-block;
            background: var(--blue-soft);
            color: var(--blue);
            border-radius: 999px;
            padding: .22rem .62rem;
            margin: .15rem .2rem .15rem 0;
            font-size: .82rem;
            font-weight: 600;
        }
        .zl-status {
            display: inline-block;
            border-radius: 999px;
            padding: .22rem .62rem;
            font-size: .8rem;
            font-weight: 700;
        }
        .zl-status-open { background: #e8f7f2; color: #08796f; }
        .zl-status-muted { background: #eef1f6; color: #596579; }
        .zl-detail-band {
            background: #eef4ff;
            border-left: 4px solid var(--blue);
            border-radius: 8px;
            padding: .9rem 1rem;
            margin: .6rem 0 1.2rem;
        }
        .zl-empty {
            background: var(--surface);
            border: 1px dashed #b9c6da;
            border-radius: 14px;
            padding: 1.5rem;
            color: var(--muted);
            text-align: center;
        }
        .zl-notification {
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 4px solid #cbd5e1;
            border-radius: 10px;
            padding: 1rem 1.1rem;
            margin: .7rem 0 .45rem;
        }
        .zl-notification-unread {
            border-left-color: var(--blue);
            background: #f8fbff;
        }
        .zl-notification-title {
            color: var(--ink);
            font-weight: 700;
            margin-bottom: .3rem;
        }
        .zl-notification-content { color: #46546a; margin-bottom: .45rem; }
        .zl-notification-time { color: var(--muted); font-size: .82rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def post_api(
    path: str,
    payload: dict,
    error_messages: dict[str, str] | None = None,
) -> dict | None:
    """Call a backend POST endpoint and show user-friendly errors."""
    try:
        response = requests.post(
            f"{BACKEND_URL}{path}",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        try:
            error_data = error.response.json()
            error_code = error_data.get("error", "request_failed")
        except (AttributeError, ValueError):
            error_code = "request_failed"
        if error_messages and error_code in error_messages:
            st.error(error_messages[error_code])
        else:
            st.error(
                f"后端请求失败（HTTP {error.response.status_code}）：{error_code}"
            )
        return None
    except requests.RequestException:
        st.error("网络异常，请稍后重试")
        return None
    except ValueError:
        st.error("后端返回的数据格式不正确")
        return None

    if not result.get("success") and result.get("status") != "ok":
        st.error(result.get("message", "操作失败，请重试"))
        return None
    return result


def get_api(
    path: str,
    show_error: bool = True,
    timeout: int = 15,
) -> dict | None:
    """Call a backend GET endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=timeout)
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if show_error:
            try:
                error_data = error.response.json()
                error_code = error_data.get("error", "request_failed")
            except (AttributeError, ValueError):
                error_code = "request_failed"
            st.error(
                f"后端请求失败（HTTP {error.response.status_code}）：{error_code}"
            )
        return None
    except requests.RequestException:
        if show_error:
            st.error("网络异常，请稍后重试")
        return None
    except ValueError:
        if show_error:
            st.error("后端返回的数据格式不正确")
        return None

    if not result.get("success") and show_error:
        st.error(result.get("message", "读取失败，请重试"))
    return result


def delete_api(path: str, params: dict | None = None) -> dict | None:
    try:
        response = requests.delete(
            f"{BACKEND_URL}{path}", params=params, timeout=30
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException:
        st.error("网络异常，请稍后重试")
        return None
    except ValueError:
        st.error("后端返回的数据格式不正确")
        return None
    if not result.get("success"):
        st.error(result.get("message", "操作失败，请重试"))
        return None
    return result


def queue_success(message: str) -> None:
    st.session_state["success_message"] = message


def show_queued_success() -> None:
    message = st.session_state.pop("success_message", None)
    if message:
        st.success(message)


def list_to_text(values: list | None) -> str:
    return "\n".join(str(value) for value in (values or []))


def text_to_list(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,，\n]", value) if item.strip()]


def set_profile_draft(data: dict, include_raw_text: bool = True) -> None:
    st.session_state["profile_draft"] = True
    if include_raw_text:
        st.session_state["profile_raw_text"] = data.get("raw_text", "") or ""
    st.session_state["profile_skills"] = list_to_text(data.get("skills"))
    st.session_state["profile_skill_levels"] = json.dumps(
        data.get("skill_levels", {}), ensure_ascii=False, indent=2
    )
    st.session_state["profile_experience"] = list_to_text(data.get("experience"))
    st.session_state["profile_interests"] = list_to_text(data.get("interests"))
    st.session_state["profile_preference"] = data.get("preference", "") or ""
    st.session_state["profile_time"] = data.get("time_commitment", "未知") or "未知"


def set_project_draft(data: dict) -> None:
    st.session_state["project_draft"] = True
    st.session_state["project_required_skills"] = list_to_text(
        data.get("required_skills")
    )
    st.session_state["project_time"] = data.get("time_requirement", "未知") or "未知"
    st.session_state["project_priority"] = list_to_text(data.get("priority"))
    st.session_state["project_type"] = data.get("project_type", "") or ""
    st.session_state["project_background"] = data.get("background", "") or ""


def set_current_user(
    user_id: int,
    username: str,
    school: str | None,
    token: str | None = None,
) -> None:
    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state["school"] = school or ""
    if token:
        st.session_state["token"] = token
    else:
        st.session_state.pop("token", None)


def navigate_to(page: str) -> None:
    st.session_state["app_page"] = page
    st.session_state.pop("selected_project_id", None)
    st.session_state.pop("project_return_page", None)


def open_project_detail(project_id: int, return_page: str) -> None:
    st.session_state["selected_project_id"] = project_id
    st.session_state["project_return_page"] = return_page


def render_page_heading(title: str, description: str) -> None:
    st.markdown(f"<div class='zl-eyebrow'>知遇 LinkLab</div>", unsafe_allow_html=True)
    st.title(title)
    st.caption(description)


def profile_completeness(profile: dict | None) -> int:
    if not profile or not profile.get("success"):
        return 0
    checks = [
        bool(profile.get("skills")),
        bool(profile.get("experience")),
        bool(profile.get("interests")),
        bool(profile.get("preference")),
        bool(profile.get("time_commitment") and profile.get("time_commitment") != "未知"),
    ]
    return round(sum(checks) / len(checks) * 100)


def load_home_overview(force: bool = False) -> dict:
    user_id = st.session_state["user_id"]
    cache_key = f"home_overview_{user_id}"
    if force or cache_key not in st.session_state:
        profile = get_api(f"/api/profile/{user_id}", show_error=False)
        projects = get_api(f"/api/my_projects/{user_id}", show_error=False)
        matches = get_api(
            f"/api/match_list/{user_id}?scope=cross_school",
            show_error=False,
            timeout=120,
        )
        st.session_state[cache_key] = {
            "profile": profile or {},
            "projects": (projects or {}).get("projects", []),
            "matches": (matches or {}).get("matches", []),
        }
    return st.session_state[cache_key]


def render_skill_pills(skills: list | None) -> None:
    values = [str(skill) for skill in (skills or []) if str(skill).strip()]
    if not values:
        st.caption("暂未填写技能")
        return
    pills = "".join(
        f"<span class='zl-pill'>{escape(skill)}</span>" for skill in values[:8]
    )
    st.markdown(pills, unsafe_allow_html=True)


def render_project_status(status: str) -> None:
    labels = {
        "recruiting": "招募中",
        "full": "已满员",
        "closed": "已关闭",
        "completed": "已完成",
    }
    css_class = "zl-status-open" if status == "recruiting" else "zl-status-muted"
    st.markdown(
        f"<span class='zl-status {css_class}'>{labels.get(status, status or '未知')}</span>",
        unsafe_allow_html=True,
    )


def render_match_breakdown(match: dict, key: str) -> None:
    """Show the three scoring dimensions as a compact visual analysis."""
    values = [
        {"维度": "技能", "得分": round(max(0.0, min(float(match.get("skill_match", 0)), 1.0)) * 100, 1)},
        {"维度": "时间", "得分": round(max(0.0, min(float(match.get("time_match", 0)), 1.0)) * 100, 1)},
        {"维度": "经验", "得分": round(max(0.0, min(float(match.get("experience_match", 0)), 1.0)) * 100, 1)},
    ]
    st.vega_lite_chart(
        {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": values},
            "mark": {"type": "bar", "cornerRadiusEnd": 5, "color": "#2764e7"},
            "encoding": {
                "y": {"field": "维度", "type": "nominal", "sort": ["技能", "时间", "经验"], "title": None},
                "x": {"field": "得分", "type": "quantitative", "scale": {"domain": [0, 100]}, "title": "得分（%）"},
                "tooltip": [
                    {"field": "维度", "type": "nominal"},
                    {"field": "得分", "type": "quantitative", "format": ".1f"},
                ],
            },
            "height": 110,
        },
        use_container_width=True,
        key=key,
    )


def render_mutual_contact(candidate_user_id: int, project_id: int) -> None:
    with st.spinner("正在读取已解锁的联系方式..."):
        result = get_api(
            f"/api/match/{candidate_user_id}/{project_id}"
            f"?viewer_id={st.session_state['user_id']}"
        )
    if not result or not result.get("mutual"):
        return

    counterpart = result.get("counterpart") or {}
    method_labels = {
        "wechat": "微信",
        "qq": "QQ",
        "phone": "手机号",
        "other": "其他联系方式",
    }
    with st.expander(
        f"联系 {counterpart.get('username') or '对方'}",
        expanded=True,
    ):
        st.markdown("**账号邮箱**")
        st.code(counterpart.get("email") or "未提供")
        contact_value = counterpart.get("contact_value") or ""
        if contact_value:
            method = method_labels.get(
                counterpart.get("contact_method"), "自选联系方式"
            )
            st.markdown(f"**{method}**")
            st.code(contact_value)
        else:
            st.caption("对方未开放额外联系方式，可先通过账号邮箱联系。")
        st.caption("联系方式仅因双方互选成功而展示，请尊重对方隐私。")


def render_candidate_card(candidate: dict, project_id: int) -> None:
    user_id = candidate.get("user_id")
    owner_status = candidate.get("owner_status", "pending")
    mutual = bool(candidate.get("mutual"))
    with st.container(border=True):
        heading, score_column = st.columns([4, 1])
        with heading:
            st.subheader(candidate.get("username") or "未命名用户")
            st.caption(
                f"{candidate.get('school') or '学校未填写'} · "
                f"{candidate.get('major') or '专业未填写'} · "
                f"{candidate.get('grade') or '年级未填写'}"
            )
        with score_column:
            st.metric("匹配度", f"{float(candidate.get('total_score', 0)):.0%}")

        skill_column, time_column, experience_column = st.columns(3)
        dimensions = (
            (skill_column, "技能匹配", candidate.get("skill_match", 0)),
            (time_column, "时间匹配", candidate.get("time_match", 0)),
            (experience_column, "经验匹配", candidate.get("experience_match", 0)),
        )
        for column, label, score in dimensions:
            with column:
                value = max(0.0, min(float(score), 1.0))
                st.caption(f"{label} {value:.0%}")
                st.progress(value)

        profile_left, profile_right = st.columns(2)
        with profile_left:
            st.markdown("**技能**")
            render_skill_pills(candidate.get("skills"))
            st.markdown("**时间投入**")
            st.write(candidate.get("time_commitment") or "未知")
        with profile_right:
            st.markdown("**经历**")
            st.write("、".join(candidate.get("experience") or []) or "未填写")
            st.markdown("**兴趣方向**")
            st.write("、".join(candidate.get("interests") or []) or "未填写")

        st.info(candidate.get("explanation") or "暂无匹配解释")
        if mutual:
            st.success("双方已匹配，联系方式已解锁")
            render_mutual_contact(user_id, project_id)
        elif owner_status == "rejected":
            st.warning("当前标记为暂不考虑，你可以随时重新选择")
        else:
            st.caption("候选人已表达意向，等待你处理")

        accept_column, decline_column = st.columns(2)
        with accept_column:
            accept_clicked = st.button(
                "已感兴趣" if owner_status == "interested" else "感兴趣",
                key=f"owner_accept_{project_id}_{user_id}",
                type="primary",
                disabled=owner_status == "interested",
                use_container_width=True,
            )
        with decline_column:
            decline_clicked = st.button(
                "已暂不考虑" if owner_status == "rejected" else "暂不考虑",
                key=f"owner_decline_{project_id}_{user_id}",
                disabled=owner_status == "rejected",
                use_container_width=True,
            )
        action = "interested" if accept_clicked else ("rejected" if decline_clicked else None)
        if action:
            with st.spinner("正在保存候选人状态..."):
                result = post_api(
                    "/api/owner_candidate_action",
                    {
                        "owner_id": st.session_state["user_id"],
                        "project_id": project_id,
                        "user_id": user_id,
                        "action": action,
                    },
                )
            if result:
                st.success("候选人状态已更新")
                st.rerun()


def render_my_match_card(match: dict) -> None:
    project_id = match.get("project_id")
    relationship_status = match.get("relationship_status", "user_interested")
    status_labels = {
        "user_interested": ("等待发起人处理", "info"),
        "mutual": ("双方已匹配", "success"),
        "owner_declined": ("发起人暂不考虑", "warning"),
    }
    status_text, status_kind = status_labels.get(
        relationship_status, ("状态待确认", "info")
    )
    with st.container(border=True):
        heading, score_column = st.columns([4, 1])
        with heading:
            st.subheader(match.get("project_name") or "未命名项目")
            st.caption(
                f"发起人：{match.get('owner_username') or '未填写'} · "
                f"{match.get('owner_school') or '学校未填写'}"
            )
        with score_column:
            st.metric("匹配度", f"{float(match.get('total_score', 0)):.0%}")

        getattr(st, status_kind)(status_text)
        dimension_columns = st.columns(3)
        for column, label, key in zip(
            dimension_columns,
            ("技能匹配", "时间匹配", "经验匹配"),
            ("skill_match", "time_match", "experience_match"),
        ):
            with column:
                value = max(0.0, min(float(match.get(key, 0)), 1.0))
                st.caption(f"{label} {value:.0%}")
                st.progress(value)
        with st.expander("查看匹配分析", expanded=False):
            render_match_breakdown(match, f"my_match_chart_{project_id}")
            st.info(match.get("explanation") or "暂无匹配解释")
        if relationship_status == "mutual":
            render_mutual_contact(
                st.session_state["user_id"],
                project_id,
            )
        st.button(
            "查看项目详情",
            key=f"my_match_detail_{project_id}",
            on_click=open_project_detail,
            args=(project_id, "我的匹配"),
        )


def show_project_detail() -> None:
    project_id = st.session_state.get("selected_project_id")
    return_page = st.session_state.get("project_return_page", "发现项目")
    if st.button("返回项目列表", key=f"back_project_{project_id}"):
        st.session_state.pop("selected_project_id", None)
        st.session_state.pop("project_return_page", None)
        st.rerun()

    with st.spinner("正在读取项目详情..."):
        project = get_api(
            f"/api/project/{project_id}?user_id={st.session_state['user_id']}"
        )
    if not project or not project.get("success"):
        return

    heading_left, heading_right = st.columns([4, 1])
    with heading_left:
        render_page_heading(
            project.get("name", "未命名项目"),
            f"由 {project.get('owner_username') or '匿名用户'} 发起",
        )
    with heading_right:
        render_project_status(project.get("status", ""))

    scope_label = (
        "同校优先" if project.get("scope") == "same_school" else "跨校开放"
    )
    created_at = str(project.get("created_at") or "")[:10] or "未知"
    st.markdown(
        f"<div class='zl-detail-band'>"
        f"{escape(project.get('owner_school') or '学校未填写')} · "
        f"{escape(scope_label)} · 发布于 {escape(created_at)}</div>",
        unsafe_allow_html=True,
    )

    summary_left, summary_right = st.columns([2, 1])
    with summary_left:
        st.subheader("项目背景与目标")
        st.write(project.get("background") or project.get("raw_text") or "暂未填写")
        if project.get("background") and project.get("raw_text"):
            st.markdown("**需求描述**")
            st.write(project.get("raw_text"))
    with summary_right:
        st.markdown("**项目类型**")
        st.write(project.get("project_type") or "未填写")
        st.markdown("**时间要求**")
        st.write(project.get("time_requirement") or "未知")
        st.markdown("**所需技能**")
        render_skill_pills(project.get("required_skills"))

    st.subheader("优先条件")
    priorities = project.get("priority") or []
    if priorities:
        for item in priorities:
            st.markdown(f"- {item}")
    else:
        st.caption("暂无额外优先条件")

    st.subheader("发起人公开信息")
    owner_columns = st.columns(3)
    owner_columns[0].metric("学校", project.get("owner_school") or "未填写")
    owner_columns[1].metric("专业", project.get("owner_major") or "未填写")
    owner_columns[2].metric("年级", project.get("owner_grade") or "未填写")

    is_owner = project.get("owner_id") == st.session_state.get("user_id")
    is_interested = bool(project.get("interested"))
    can_apply = (
        project.get("status") == "recruiting" and not is_owner and not is_interested
    )
    if st.button(
        (
            "感兴趣"
            if can_apply
            else (
                "已感兴趣"
                if is_interested
                else ("这是我发布的项目" if is_owner else "当前不可申请")
            )
        ),
        key=f"detail_interest_{project_id}_{return_page}",
        type="primary",
        disabled=not can_apply,
    ):
        with st.spinner("正在保存感兴趣状态..."):
            result = post_api(
                "/api/interest",
                {"user_id": st.session_state["user_id"], "project_id": project_id},
            )
        if result:
            st.success("已记录你的意向")

    favorited = bool(project.get("favorited"))
    if st.button(
        "已收藏" if favorited else "收藏项目",
        key=f"detail_favorite_{project_id}_{return_page}",
        disabled=favorited,
    ):
        with st.spinner("正在保存收藏..."):
            result = post_api(
                "/api/favorites",
                {"user_id": st.session_state["user_id"], "project_id": project_id},
            )
        if result and result.get("favorited"):
            st.success("已加入收藏")
            st.rerun()


def render_match_card(match: dict, *, source: str) -> None:
    project_id = match.get("project_id")
    is_interested = bool(match.get("interested")) or match.get("status") == "interested"
    total_score = max(0.0, min(float(match.get("total_score", 0)), 1.0))
    skill_match = max(0.0, min(float(match.get("skill_match", 0)), 1.0))
    time_match = max(0.0, min(float(match.get("time_match", 0)), 1.0))
    experience_match = max(0.0, min(float(match.get("experience_match", 0)), 1.0))

    with st.container(border=True):
        title_column, score_column = st.columns([4, 1])
        with title_column:
            st.subheader(match.get("project_name", "未命名项目"))
            school = match.get("owner_school") or "学校未填写"
            scope = "同校优先" if match.get("scope") == "same_school" else "跨校开放"
            st.caption(f"{school} · {scope}")
        with score_column:
            st.metric("综合匹配度", f"{total_score:.0%}")

        skill_column, time_column, experience_column = st.columns(3)
        dimensions = (
            (skill_column, "技能匹配", skill_match),
            (time_column, "时间匹配", time_match),
            (experience_column, "经验匹配", experience_match),
        )
        for column, label, score in dimensions:
            with column:
                st.caption(f"{label} {score:.0%}")
                st.progress(score)

        with st.expander("查看匹配分析", expanded=False):
            render_match_breakdown(match, f"{source}_match_chart_{project_id}")
            st.info(match.get("explanation") or "暂无匹配解释")
        action_left, action_right = st.columns([1, 3])
        with action_left:
            if st.button(
                "已感兴趣" if is_interested else "感兴趣",
                key=f"{source}_interest_{project_id}",
                type="primary",
                disabled=is_interested,
                use_container_width=True,
            ):
                if project_id is None:
                    st.error("项目信息不完整，请刷新后重试")
                else:
                    with st.spinner("正在保存感兴趣状态..."):
                        result = post_api(
                            "/api/interest",
                            {
                                "user_id": st.session_state["user_id"],
                                "project_id": project_id,
                            },
                        )
                    if result and result.get("interested"):
                        match["interested"] = True
                        match["status"] = "interested"
                        st.success("已记录你的意向")
                        st.rerun()
        with action_right:
            st.button(
                "查看详情",
                key=f"{source}_detail_{project_id}",
                on_click=open_project_detail,
                args=(project_id, "首页" if source == "home" else "匹配推荐"),
                use_container_width=True,
            )


def render_project_card(project: dict) -> None:
    project_id = project.get("project_id")
    with st.container(border=True):
        heading, score_column = st.columns([4, 1])
        with heading:
            st.subheader(project.get("name") or "未命名项目")
            scope_label = (
                "同校优先"
                if project.get("scope") == "same_school"
                else "跨校开放"
            )
            project_type = project.get("project_type") or "类型未填写"
            st.caption(
                f"{project.get('owner_school') or '学校未填写'} · "
                f"{project_type} · {scope_label}"
            )
        with score_column:
            if project.get("total_score") is not None:
                st.metric("匹配度", f"{float(project['total_score']):.0%}")
            else:
                render_project_status(project.get("status", ""))

        description = project.get("background") or project.get("raw_text") or "暂无项目描述"
        st.write(description[:180] + ("..." if len(description) > 180 else ""))
        render_skill_pills(project.get("required_skills"))
        st.caption(
            f"时间要求：{project.get('time_requirement') or '未知'} · "
            f"发布于 {str(project.get('created_at') or '')[:10] or '未知'}"
        )

        detail_column, interest_column, favorite_column, status_column = st.columns([1, 1, 1, 2])
        with detail_column:
            st.button(
                "查看详情",
                key=f"discover_detail_{project_id}",
                on_click=open_project_detail,
                args=(project_id, "发现项目"),
                use_container_width=True,
            )
        with interest_column:
            is_owner = project.get("owner_id") == st.session_state.get("user_id")
            is_interested = bool(project.get("interested"))
            can_apply = project.get("status") == "recruiting" and not is_owner
            if st.button(
                "已感兴趣" if is_interested else "感兴趣",
                key=f"discover_interest_{project_id}",
                type="primary",
                disabled=is_interested or not can_apply,
                use_container_width=True,
            ):
                with st.spinner("正在保存感兴趣状态..."):
                    result = post_api(
                        "/api/interest",
                        {
                            "user_id": st.session_state["user_id"],
                            "project_id": project_id,
                        },
                    )
                if result:
                    st.success("已记录你的意向")
                    st.rerun()
        with favorite_column:
            favorited = bool(project.get("favorited"))
            if st.button(
                "已收藏" if favorited else "收藏",
                key=f"discover_favorite_{project_id}",
                disabled=favorited,
                use_container_width=True,
            ):
                with st.spinner("正在保存收藏..."):
                    result = post_api(
                        "/api/favorites",
                        {
                            "user_id": st.session_state["user_id"],
                            "project_id": project_id,
                        },
                    )
                if result and result.get("favorited"):
                    st.success("已加入收藏")
                    st.rerun()
        with status_column:
            if project.get("total_score") is not None:
                render_project_status(project.get("status", ""))


def show_home_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "首页"
    ):
        show_project_detail()
        return

    username = st.session_state.get("username", "同学")
    school = st.session_state.get("school") or "高校科研社区"
    st.markdown(
        f"""
        <section class="zl-hero">
            <div class="zl-eyebrow" style="color:#83c9ff">RESEARCH COLLABORATION</div>
            <h1>你好，{username}</h1>
            <p>{school} · 用能力画像连接合适的项目与科研搭档。</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("正在整理你的协作概览..."):
        overview = load_home_overview()
    completeness = profile_completeness(overview["profile"])
    projects = overview["projects"]
    matches = overview["matches"]
    interested_count = sum(
        1 for item in matches if item.get("interested") or item.get("status") == "interested"
    )

    metric_columns = st.columns(4)
    metrics = (
        ("画像完整度", f"{completeness}%"),
        ("推荐项目", str(len(matches))),
        ("我发布的项目", str(len(projects))),
        ("已表达意向", str(interested_count)),
    )
    for column, (label, value) in zip(metric_columns, metrics):
        with column:
            st.metric(label, value)

    st.markdown(
        "<div class='zl-section'><div class='zl-section-title'>快速开始</div>"
        "<div class='zl-section-caption'>从完善画像到建立连接，只需要三个步骤。</div></div>",
        unsafe_allow_html=True,
    )
    quick_columns = st.columns(3)
    quick_actions = (
        (quick_columns[0], "完善能力画像", "让系统更准确地理解你的技能与经历", "我的画像"),
        (quick_columns[1], "发现科研项目", "浏览同校与跨校开放的合作机会", "发现项目"),
        (quick_columns[2], "发布招募需求", "把项目需求转换成清晰的结构化标签", "发布项目"),
    )
    for column, title, description, page in quick_actions:
        with column:
            with st.container(border=True):
                st.subheader(title)
                st.caption(description)
                st.button(
                    "进入",
                    key=f"home_go_{page}",
                    on_click=navigate_to,
                    args=(page,),
                    use_container_width=True,
                )

    st.markdown(
        "<div class='zl-section'><div class='zl-section-title'>优先推荐</div>"
        "<div class='zl-section-caption'>根据你的画像展示当前得分最高的项目。</div></div>",
        unsafe_allow_html=True,
    )
    if matches:
        for match in matches[:2]:
            render_match_card(match, source="home")
    else:
        st.markdown(
            "<div class='zl-empty'>暂无推荐项目。完善画像后再来看看，或者先发布一个项目。</div>",
            unsafe_allow_html=True,
        )

    if st.button("刷新概览", key="refresh_home"):
        load_home_overview(force=True)
        st.rerun()


def show_discover_projects_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "发现项目"
    ):
        show_project_detail()
        return

    render_page_heading("发现项目", "浏览同校与跨校科研机会，快速找到值得进一步了解的方向。")
    keyword = st.text_input(
        "搜索项目",
        placeholder="搜索项目名称、描述、学校或技能",
    ).strip()
    school_column, type_column, skill_column = st.columns(3)
    with school_column:
        school = st.text_input("学校", placeholder="例如：华东师范大学").strip()
    with type_column:
        project_type = st.text_input("项目类型", placeholder="例如：大模型应用").strip()
    with skill_column:
        skill = st.text_input("所需技能", placeholder="例如：Python").strip()

    scope_column, status_column, sort_column = st.columns(3)
    with scope_column:
        scope_label = st.selectbox("开放范围", ["全部范围", "同校优先", "跨校开放"])
    with status_column:
        status_label = st.selectbox(
            "招募状态", ["招募中", "全部状态", "已满员", "已关闭", "已完成"]
        )
    with sort_column:
        sort_label = st.selectbox("排序", ["最新发布", "匹配度优先"])

    scope_map = {"全部范围": "", "同校优先": "same_school", "跨校开放": "cross_school"}
    status_map = {
        "全部状态": "all",
        "招募中": "recruiting",
        "已满员": "full",
        "已关闭": "closed",
        "已完成": "completed",
    }
    page = int(st.session_state.get("discover_page", 1))
    query = urlencode(
        {
            "keyword": keyword,
            "school": school,
            "project_type": project_type,
            "skill": skill,
            "scope": scope_map[scope_label],
            "status": status_map[status_label],
            "sort": "match" if sort_label == "匹配度优先" else "latest",
            "page": page,
            "page_size": 8,
            "user_id": st.session_state["user_id"],
        }
    )
    with st.spinner("正在搜索项目..."):
        result = get_api(f"/api/projects?{query}")
    if not result or not result.get("success"):
        return

    projects = result.get("projects", [])
    pagination = result.get("pagination", {})
    total = int(pagination.get("total", len(projects)))
    total_pages = max(int(pagination.get("total_pages", 1)), 1)
    if page > total_pages:
        st.session_state["discover_page"] = total_pages
        st.rerun()

    st.caption(f"找到 {total} 个符合条件的项目 · 第 {page}/{total_pages} 页")
    if not projects:
        st.markdown(
            "<div class='zl-empty'>没有符合当前条件的项目，可以尝试清空关键词或切换范围。</div>",
            unsafe_allow_html=True,
        )
        return
    for project in projects:
        render_project_card(project)

    previous_column, page_column, next_column = st.columns([1, 2, 1])
    with previous_column:
        if st.button("上一页", disabled=page <= 1, use_container_width=True):
            st.session_state["discover_page"] = page - 1
            st.rerun()
    with page_column:
        st.markdown(
            f"<div style='text-align:center;padding:.65rem;color:#667085'>"
            f"第 {page} 页，共 {total_pages} 页</div>",
            unsafe_allow_html=True,
        )
    with next_column:
        if st.button("下一页", disabled=page >= total_pages, use_container_width=True):
            st.session_state["discover_page"] = page + 1
            st.rerun()


def show_auth_page() -> None:
    st.title("知遇LinkLab - 找到你的科研搭档")
    login_tab, register_tab = st.tabs(["登录", "注册"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("用户名", key="login_username")
            password = st.text_input(
                "密码",
                type="password",
                key="login_password",
            )
            submitted = st.form_submit_button("登录", use_container_width=True)

        if submitted:
            if not username.strip() or not password:
                st.warning("请输入用户名和密码")
            else:
                with st.spinner("正在登录..."):
                    result = post_api(
                        "/api/auth/login",
                        {
                            "username": username.strip(),
                            "password": password,
                        },
                        error_messages={
                            "user_not_found": "用户不存在",
                            "invalid_password": "密码错误",
                        },
                    )
                if result:
                    token = result.get("token")
                    if not token:
                        st.error("登录成功但未获取到 token")
                    else:
                        set_current_user(
                            result["user_id"],
                            result["username"],
                            result.get("school"),
                            token,
                        )
                        queue_success("登录成功")
                        st.rerun()

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("用户名", key="register_username")
            email = st.text_input("邮箱", key="register_email")
            password = st.text_input(
                "密码",
                type="password",
                key="register_password",
            )
            confirm_password = st.text_input(
                "确认密码",
                type="password",
                key="register_confirm_password",
            )
            school = st.text_input("学校", key="register_school")
            major = st.text_input("专业", key="register_major")
            grade = st.text_input("年级", key="register_grade")
            submitted = st.form_submit_button("注册", use_container_width=True)

        if submitted:
            if (
                not username.strip()
                or not email.strip()
                or not password
                or not confirm_password
            ):
                st.warning("用户名、邮箱和密码不能为空")
            elif password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                with st.spinner("正在注册..."):
                    result = post_api(
                        "/api/auth/register",
                        {
                            "username": username.strip(),
                            "email": email.strip(),
                            "password": password,
                            "confirm_password": confirm_password,
                            "school": school.strip(),
                            "major": major.strip(),
                            "grade": grade.strip(),
                        },
                    )
                if result:
                    st.success("注册成功，请使用用户名和密码登录")


def show_profile_page() -> None:
    st.header("我的画像")
    user_id = st.session_state["user_id"]
    loaded_key = f"profile_loaded_{user_id}"

    if not st.session_state.get(loaded_key):
        with st.spinner("正在读取画像..."):
            existing = get_api(f"/api/profile/{user_id}")
        if existing is not None:
            st.session_state[loaded_key] = True
            if existing.get("success"):
                set_profile_draft(existing)
                st.success("画像加载成功")

    contact_loaded_key = f"contact_loaded_{user_id}"
    if not st.session_state.get(contact_loaded_key):
        with st.spinner("正在读取联系方式设置..."):
            contact_data = get_api(f"/api/profile/{user_id}", show_error=False)
        st.session_state["contact_method"] = (
            (contact_data or {}).get("contact_method") or ""
        )
        st.session_state["contact_value"] = (
            (contact_data or {}).get("contact_value") or ""
        )
        st.session_state["contact_visible"] = bool(
            (contact_data or {}).get("contact_visible", False)
        )
        st.session_state[contact_loaded_key] = True

    raw_text = st.text_area(
        "自然语言描述",
        placeholder="请描述你的技能、经历、兴趣、协作偏好和每周可投入时间",
        height=160,
        key="profile_raw_text",
    )

    if st.button("解析", key="parse_profile_button"):
        if not raw_text.strip():
            st.warning("请先输入个人描述")
        else:
            with st.spinner("AI正在解析中..."):
                result = post_api("/api/parse_profile", {"raw_text": raw_text})
            if result:
                parsed_data = result.get("data", {})
                set_profile_draft(parsed_data, include_raw_text=False)
                queue_success("画像解析成功")
                st.rerun()

    if st.session_state.get("profile_draft"):
        st.subheader("画像内容")
        left, right = st.columns(2)
        with left:
            st.text_area("技能（一行一项）", key="profile_skills", height=130)
            st.text_area("项目经历（一行一项）", key="profile_experience", height=130)
            st.text_input("协作偏好", key="profile_preference")
        with right:
            st.text_area(
                "技能等级（JSON对象）",
                key="profile_skill_levels",
                height=130,
            )
            st.text_area("兴趣方向（一行一项）", key="profile_interests", height=130)
            st.text_input("时间投入", key="profile_time")

        if st.button("保存画像", type="primary", use_container_width=True):
            try:
                skill_levels = json.loads(st.session_state["profile_skill_levels"])
                if not isinstance(skill_levels, dict):
                    raise ValueError
            except (json.JSONDecodeError, ValueError):
                st.error("技能等级必须是JSON对象，例如 {\"Python\": \"熟练\"}")
            else:
                parsed_data = {
                    "skills": text_to_list(st.session_state["profile_skills"]),
                    "skill_levels": skill_levels,
                    "experience": text_to_list(st.session_state["profile_experience"]),
                    "interests": text_to_list(st.session_state["profile_interests"]),
                    "preference": st.session_state["profile_preference"].strip(),
                    "time_commitment": st.session_state["profile_time"].strip(),
                }
                with st.spinner("正在保存画像..."):
                    result = post_api(
                        "/api/save_profile",
                        {
                            "user_id": user_id,
                            "raw_text": st.session_state["profile_raw_text"],
                            "parsed_data": parsed_data,
                        },
                    )
                if result:
                    st.success("画像保存成功")

    st.divider()
    st.subheader("匹配后的联系方式")
    st.caption(
        "账号邮箱只会在双方互选成功后向对方展示。你还可以选择开放一种额外联系方式。"
    )
    contact_labels = {
        "": "不填写",
        "wechat": "微信",
        "qq": "QQ",
        "phone": "手机号",
        "other": "其他",
    }
    with st.form("contact_settings_form"):
        st.selectbox(
            "联系方式类型",
            list(contact_labels),
            format_func=lambda value: contact_labels[value],
            key="contact_method",
        )
        st.text_input(
            "联系方式内容",
            placeholder="填写微信号、QQ号、手机号或其他联系方式",
            key="contact_value",
        )
        st.checkbox(
            "双方匹配后允许向对方展示这项联系方式",
            key="contact_visible",
        )
        save_contact = st.form_submit_button(
            "保存联系方式设置",
            type="primary",
            use_container_width=True,
        )
    if save_contact:
        method = st.session_state["contact_method"]
        value = st.session_state["contact_value"].strip()
        if value and not method:
            st.error("填写联系方式内容后，请选择对应类型")
        else:
            with st.spinner("正在保存联系方式设置..."):
                result = post_api(
                    "/api/profile/contact",
                    {
                        "user_id": user_id,
                        "contact_method": method,
                        "contact_value": value,
                        "contact_visible": st.session_state["contact_visible"],
                    },
                )
            if result:
                st.success("联系方式设置已保存")


def show_publish_project_page() -> None:
    st.header("发布项目")
    project_name = st.text_input("项目名称", key="new_project_name")
    raw_text = st.text_area(
        "需求描述",
        placeholder="请描述项目背景、所需技能、时间要求和优先条件",
        height=160,
        key="new_project_raw_text",
    )
    scope_label = st.radio(
        "开放范围",
        ["同校优先", "接受跨校"],
        horizontal=True,
        key="new_project_scope",
    )

    if st.button("解析", key="parse_project_button"):
        if not raw_text.strip():
            st.warning("请先输入项目需求")
        else:
            with st.spinner("AI正在解析中..."):
                result = post_api("/api/parse_project", {"raw_text": raw_text})
            if result:
                set_project_draft(result.get("data", {}))
                queue_success("项目需求解析成功")
                st.rerun()

    if st.session_state.get("project_draft"):
        st.subheader("项目需求")
        left, right = st.columns(2)
        with left:
            st.text_area(
                "所需技能（一行一项）",
                key="project_required_skills",
                height=130,
            )
            st.text_area("优先条件（一行一项）", key="project_priority", height=130)
            st.text_input("项目类型", key="project_type")
        with right:
            st.text_input("时间要求", key="project_time")
            st.text_area("项目背景", key="project_background", height=210)

        if st.button("发布项目", type="primary", use_container_width=True):
            if not project_name.strip():
                st.warning("请填写项目名称")
            else:
                parsed_data = {
                    "required_skills": text_to_list(
                        st.session_state["project_required_skills"]
                    ),
                    "time_requirement": st.session_state["project_time"].strip(),
                    "priority": text_to_list(st.session_state["project_priority"]),
                    "project_type": st.session_state["project_type"].strip(),
                    "background": st.session_state["project_background"].strip(),
                }
                with st.spinner("正在发布项目..."):
                    result = post_api(
                        "/api/create_project",
                        {
                            "owner_id": st.session_state["user_id"],
                            "name": project_name.strip(),
                            "raw_text": raw_text,
                            "parsed_data": parsed_data,
                            "scope": (
                                "same_school"
                                if scope_label == "同校优先"
                                else "cross_school"
                            ),
                        },
                    )
                if result:
                    st.success(f"项目发布成功，项目ID：{result['project_id']}")


def show_match_recommendations_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "匹配推荐"
    ):
        show_project_detail()
        return

    st.header("为你推荐的匹配项目")
    success_message = st.session_state.pop("interest_success_message", None)
    if success_message:
        st.success(success_message)

    scope_label = st.radio(
        "推荐范围",
        ["同校优先", "跨校开放"],
        horizontal=True,
        key="match_scope",
    )
    scope = "same_school" if scope_label == "同校优先" else "cross_school"

    with st.spinner("正在计算匹配度..."):
        result = get_api(
            f"/api/match_list/{st.session_state['user_id']}?scope={scope}",
            timeout=120,
        )

    if result is None or not result.get("success"):
        return

    matches = result.get("matches", [])
    if not matches:
        st.info("暂时没有适合的项目，请先完善画像或等待更多项目发布")
        return

    st.success(f"匹配成功，共找到 {len(matches)} 个项目")
    for match in matches:
        render_match_card(match, source="recommendation")


def show_my_matches_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "我的匹配"
    ):
        show_project_detail()
        return

    render_page_heading("我的匹配", "查看你表达过意向的项目和发起人的处理结果。")
    with st.spinner("正在读取匹配进度..."):
        result = get_api(f"/api/my_matches/{st.session_state['user_id']}")
    if result is None or not result.get("success"):
        return
    matches = result.get("matches", [])
    if not matches:
        st.markdown(
            "<div class='zl-empty'>你还没有对项目表达意向，可以先去发现项目。</div>",
            unsafe_allow_html=True,
        )
        return

    counts = {
        "mutual": sum(item.get("relationship_status") == "mutual" for item in matches),
        "pending": sum(
            item.get("relationship_status") == "user_interested" for item in matches
        ),
        "declined": sum(
            item.get("relationship_status") == "owner_declined" for item in matches
        ),
    }
    metric_columns = st.columns(3)
    metric_columns[0].metric("双方已匹配", counts["mutual"])
    metric_columns[1].metric("等待处理", counts["pending"])
    metric_columns[2].metric("暂不考虑", counts["declined"])
    for match in matches:
        render_my_match_card(match)


def show_notifications_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "通知"
    ):
        show_project_detail()
        return

    render_page_heading("通知中心", "集中查看申请进度、互选结果与项目状态变化。")
    user_id = st.session_state["user_id"]
    unread_only = st.segmented_control(
        "通知范围",
        options=["全部通知", "仅看未读"],
        default="全部通知",
        key="notification_filter",
    )
    query = "?unread_only=true" if unread_only == "仅看未读" else ""
    with st.spinner("正在读取通知..."):
        result = get_api(f"/api/notifications/{user_id}{query}")
    if result is None or not result.get("success"):
        return

    notifications = result.get("notifications", [])
    unread_count = int(result.get("unread_count", 0))
    heading, action = st.columns([4, 1])
    heading.metric("未读通知", unread_count)
    if action.button(
        "全部标记已读",
        use_container_width=True,
        disabled=unread_count == 0,
    ):
        with st.spinner("正在更新通知状态..."):
            update_result = post_api(
                "/api/notifications/read-all",
                {"user_id": user_id},
            )
        if update_result and update_result.get("success"):
            st.success("全部通知已标记为已读")
            st.rerun()

    if not notifications:
        message = "目前没有未读通知" if unread_only == "仅看未读" else "目前还没有通知"
        st.markdown(f"<div class='zl-empty'>{message}</div>", unsafe_allow_html=True)
        return

    for item in notifications:
        notification_id = item.get("notification_id")
        is_read = bool(item.get("is_read"))
        css_class = "zl-notification" if is_read else "zl-notification zl-notification-unread"
        created_at = str(item.get("created_at") or "").replace("T", " ")[:16]
        st.markdown(
            f"""
            <div class='{css_class}'>
                <div class='zl-notification-title'>{escape(str(item.get('title') or '通知'))}</div>
                <div class='zl-notification-content'>{escape(str(item.get('content') or ''))}</div>
                <div class='zl-notification-time'>{escape(created_at or '时间未知')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        controls = st.columns([1, 1, 4])
        project_id = item.get("related_project_id")
        if project_id:
            controls[0].button(
                "查看项目",
                key=f"notification_project_{notification_id}",
                on_click=open_project_detail,
                args=(int(project_id), "通知"),
                use_container_width=True,
            )
        if not is_read and controls[1].button(
            "标记已读",
            key=f"notification_read_{notification_id}",
            use_container_width=True,
        ):
            with st.spinner("正在更新通知状态..."):
                update_result = post_api(
                    f"/api/notifications/{notification_id}/read",
                    {"user_id": user_id},
                )
            if update_result and update_result.get("success"):
                st.success("通知已标记为已读")
                st.rerun()


def show_my_projects_page() -> None:
    st.header("我的项目")
    with st.spinner("正在读取项目列表..."):
        result = get_api(f"/api/my_projects/{st.session_state['user_id']}")
    if result is None or not result.get("success"):
        return

    projects = result.get("projects", [])
    if not projects:
        st.info("你还没有发布项目")
        return

    st.success(f"共读取到 {len(projects)} 个项目")
    status_labels = {
        "recruiting": "招募中",
        "full": "已满员",
        "closed": "已关闭",
        "completed": "已完成",
    }
    scope_labels = {
        "same_school": "同校优先",
        "cross_school": "接受跨校",
    }

    for project in projects:
        status = status_labels.get(project.get("status"), project.get("status", "未知"))
        created_at = project.get("created_at") or "未知日期"
        with st.expander(f"{project.get('name', '未命名项目')}  |  {status}  |  {created_at}"):
            if project.get("moderation_status") == "removed":
                st.error("该项目已被平台下架，暂不对其他用户展示。")
                if project.get("moderation_reason"):
                    st.warning(f"处理原因：{project['moderation_reason']}")
            st.caption(
                f"发布时间：{created_at} · "
                f"开放范围：{scope_labels.get(project.get('scope'), '未设置')}"
            )

            required_skills = project.get("required_skills") or []
            st.markdown("**所需技能**")
            st.write("、".join(str(skill) for skill in required_skills) or "未填写")

            left, right = st.columns(2)
            with left:
                st.markdown("**项目类型**")
                st.write(project.get("project_type") or "未填写")
                st.markdown("**时间要求**")
                st.write(project.get("time_requirement") or "未知")
            with right:
                st.markdown("**优先条件**")
                priority = project.get("priority") or []
                st.write("、".join(str(item) for item in priority) or "无")
                st.markdown("**当前状态**")
                st.write(status)

            st.markdown("**项目背景**")
            st.write(project.get("background") or "未填写")
            st.markdown("**原始需求描述**")
            st.write(project.get("raw_text") or "未填写")

            st.markdown("**候选人管理**")
            with st.spinner("正在读取候选人..."):
                candidates_result = get_api(
                    f"/api/project/{project.get('project_id')}/candidates"
                    f"?owner_id={st.session_state['user_id']}"
                )
            if candidates_result is None or not candidates_result.get("success"):
                continue
            candidates = candidates_result.get("candidates", [])
            if not candidates:
                st.caption("暂时还没有用户对这个项目表达感兴趣")
            else:
                st.caption(f"共有 {len(candidates)} 位候选人表达了意向")
                for candidate in candidates:
                    render_candidate_card(candidate, project.get("project_id"))


def show_favorites_page() -> None:
    if (
        st.session_state.get("selected_project_id")
        and st.session_state.get("project_return_page") == "我的收藏"
    ):
        show_project_detail()
        return
    render_page_heading("我的收藏", "把值得进一步了解的项目集中保存。")
    with st.spinner("正在读取收藏..."):
        result = get_api(f"/api/favorites/{st.session_state['user_id']}")
    if result is None or not result.get("success"):
        return
    favorites = result.get("favorites", [])
    if not favorites:
        st.markdown(
            "<div class='zl-empty'>还没有收藏项目，可以先去发现项目。</div>",
            unsafe_allow_html=True,
        )
        return
    st.success(f"已收藏 {len(favorites)} 个项目")
    for favorite in favorites:
        project_id = favorite.get("project_id")
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.subheader(favorite.get("name") or "未命名项目")
                st.caption(
                    f"{favorite.get('owner_school') or '学校未填写'} · "
                    f"{favorite.get('project_type') or '类型未填写'} · "
                    f"{favorite.get('status') or '未知状态'}"
                )
                render_skill_pills(favorite.get("required_skills"))
                st.write(
                    (favorite.get("raw_text") or "暂无项目描述")[:180]
                )
            with right:
                st.button(
                    "查看详情",
                    key=f"favorite_detail_{project_id}",
                    on_click=open_project_detail,
                    args=(project_id, "我的收藏"),
                    use_container_width=True,
                )
                if st.button(
                    "取消收藏",
                    key=f"favorite_remove_{project_id}",
                    use_container_width=True,
                ):
                    with st.spinner("正在取消收藏..."):
                        removed = delete_api(
                            f"/api/favorites/{project_id}",
                            {"user_id": st.session_state["user_id"]},
                        )
                    if removed and not removed.get("favorited"):
                        st.success("已取消收藏")
                        st.rerun()


def show_feedback_page() -> None:
    render_page_heading("意见反馈", "你的反馈会帮助平台持续改进匹配体验。")
    categories = ["功能建议", "匹配不准确", "使用问题", "内容举报", "账号问题", "其他"]
    with st.form("feedback_form"):
        category = st.selectbox("反馈类型", categories)
        content = st.text_area(
            "反馈内容",
            placeholder="请描述遇到的问题或希望改进的地方",
            height=150,
        )
        contact_email = st.text_input("联系邮箱（可选）")
        submitted = st.form_submit_button("提交反馈", type="primary")
    if submitted:
        with st.spinner("正在提交反馈..."):
            result = post_api(
                "/api/feedback",
                {
                    "user_id": st.session_state["user_id"],
                    "category": category,
                    "content": content,
                    "contact_email": contact_email,
                    "source_page": st.session_state.get("app_page", "意见反馈"),
                },
            )
        if result:
            st.success("反馈已提交，感谢你的建议")

    st.markdown("### 我的反馈记录")
    with st.spinner("正在读取反馈记录..."):
        result = get_api(f"/api/my_feedback/{st.session_state['user_id']}")
    if result is None or not result.get("success"):
        return
    status_labels = {
        "pending": "待处理",
        "reviewing": "处理中",
        "resolved": "已处理",
        "rejected": "已驳回",
    }
    feedbacks = result.get("feedback", [])
    if not feedbacks:
        st.caption("你还没有提交过反馈")
        return
    for item in feedbacks:
        with st.expander(
            f"{item.get('category', '其他')} · "
            f"{status_labels.get(item.get('status'), '未知')} · "
            f"{str(item.get('created_at') or '')[:10]}"
        ):
            st.write(item.get("content") or "")
            if item.get("admin_reply"):
                st.info(f"管理员回复：{item['admin_reply']}")


def show_authenticated_app() -> None:
    show_queued_success()
    notification_summary = get_api(
        f"/api/notifications/{st.session_state['user_id']}?unread_only=true&page_size=1",
        show_error=False,
        timeout=5,
    )
    unread_count = (
        int(notification_summary.get("unread_count", 0))
        if notification_summary and notification_summary.get("success")
        else 0
    )
    with st.sidebar:
        st.markdown("### 知遇 **LinkLab**")
        st.caption("科研协作匹配平台")
        st.divider()
        st.subheader(st.session_state["username"])
        school = st.session_state.get("school")
        if school:
            st.caption(school)

        pages = [
            "首页",
            "发现项目",
            "匹配推荐",
            "我的匹配",
            "通知",
            "我的收藏",
            "意见反馈",
            "我的画像",
            "发布项目",
            "我的项目",
        ]
        current_page = st.session_state.get("app_page", "首页")
        if current_page not in pages:
            current_page = "首页"
        navigation_labels = {
            item: f"通知 ({unread_count})" if item == "通知" and unread_count else item
            for item in pages
        }
        page = st.radio(
            "页面导航",
            pages,
            index=pages.index(current_page),
            key="app_page",
            format_func=lambda item: navigation_labels[item],
        )

        st.divider()
        if st.button("退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    pages = {
        "首页": show_home_page,
        "发现项目": show_discover_projects_page,
        "我的画像": show_profile_page,
        "发布项目": show_publish_project_page,
        "匹配推荐": show_match_recommendations_page,
        "我的匹配": show_my_matches_page,
        "通知": show_notifications_page,
        "我的收藏": show_favorites_page,
        "意见反馈": show_feedback_page,
        "我的项目": show_my_projects_page,
    }
    pages[page]()


def main() -> None:
    st.set_page_config(
        page_title="知遇LinkLab - 找到你的科研搭档",
        page_icon="🔗",
        layout="wide",
    )
    inject_styles()

    if st.session_state.get("user_id"):
        show_authenticated_app()
    else:
        show_auth_page()


if __name__ == "__main__":
    main()
