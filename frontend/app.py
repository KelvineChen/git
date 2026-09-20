import json
import re

import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"


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
        st.error("无法连接后端，请确认后端服务已启动")
        return None
    except ValueError:
        st.error("后端返回的数据格式不正确")
        return None

    if not result.get("success") and result.get("status") != "ok":
        st.error(result.get("message", "操作失败，请重试"))
        return None
    return result


def get_api(path: str, show_error: bool = True) -> dict | None:
    """Call a backend GET endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=15)
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
            st.error("无法连接后端，请确认后端服务已启动")
        return None
    except ValueError:
        if show_error:
            st.error("后端返回的数据格式不正确")
        return None

    if not result.get("success") and show_error:
        st.error(result.get("message", "读取失败，请重试"))
    return result


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
        existing = get_api(f"/api/profile/{user_id}", show_error=False)
        if existing is not None:
            st.session_state[loaded_key] = True
            if existing.get("success"):
                set_profile_draft(existing)

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
    st.header("匹配推荐")
    st.write("这里是匹配推荐页")


def show_my_projects_page() -> None:
    st.header("我的项目")
    st.write("这里是我的项目页")


def show_authenticated_app() -> None:
    with st.sidebar:
        st.subheader(st.session_state["username"])
        school = st.session_state.get("school")
        if school:
            st.caption(school)

        page = st.radio(
            "页面导航",
            ["我的画像", "发布项目", "匹配推荐", "我的项目"],
        )

        if st.button("退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    pages = {
        "我的画像": show_profile_page,
        "发布项目": show_publish_project_page,
        "匹配推荐": show_match_recommendations_page,
        "我的项目": show_my_projects_page,
    }
    pages[page]()


def main() -> None:
    st.set_page_config(
        page_title="知遇LinkLab - 找到你的科研搭档",
        page_icon="🔗",
        layout="wide",
    )

    if st.session_state.get("user_id"):
        show_authenticated_app()
    else:
        show_auth_page()


if __name__ == "__main__":
    main()
