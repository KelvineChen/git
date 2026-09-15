import json

import requests
import streamlit as st


BACKEND_URL = "http://localhost:8000"


def call_api(path: str, payload: dict) -> dict | None:
    try:
        response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if not result.get("success"):
            st.error(result.get("message", "接口调用失败，请重试"))
            return None
        return result.get("data", result)
    except requests.RequestException:
        st.error("无法连接后端，请确认后端服务已启动")
    except ValueError:
        st.error("后端返回的数据格式不正确")
    return None


def show_tags(title: str, values: list) -> None:
    st.markdown(f"**{title}**")
    if values:
        st.markdown(" ".join(f"`{value}`" for value in values))
    else:
        st.caption("暂无")


st.set_page_config(page_title="知遇LinkLab - 找到你的科研搭档")
st.title("知遇LinkLab - 找到你的科研搭档")

try:
    health_response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    health_response.raise_for_status()
    st.success("后端连接正常")
except requests.RequestException:
    st.error("后端未启动，请先启动后端服务")

profile_tab, project_tab, match_tab = st.tabs(["能力画像", "项目发布", "匹配测试"])

with profile_tab:
    st.header("能力画像")
    raw_text = st.text_area(
        "用户描述",
        placeholder="请用自然语言描述你的技能、经历和协作偏好",
        height=180,
        key="profile_text",
    )
    if st.button("解析", key="profile_button"):
        if not raw_text.strip():
            st.warning("请先输入用户描述")
        else:
            with st.spinner("AI正在解析中..."):
                data = call_api("/api/parse_profile", {"raw_text": raw_text})
            if data:
                st.json(data)

with project_tab:
    st.header("项目发布")
    project_name = st.text_input("项目名称")
    project_text = st.text_area(
        "需求描述",
        placeholder="请描述项目背景、所需技能、时间要求和优先条件",
    )
    if st.button("解析", key="project_button"):
        if not project_name.strip() or not project_text.strip():
            st.warning("请填写项目名称和需求描述")
        else:
            with st.spinner("AI正在解析中..."):
                data = call_api("/api/parse_project", {"raw_text": project_text})
            if data:
                st.subheader("解析结果")
                st.json(data)

with match_tab:
    st.header("匹配测试")
    user_column, project_column = st.columns(2)

    with user_column:
        st.subheader("用户画像")
        match_user_text = st.text_area(
            "用户自然语言或 JSON",
            placeholder="输入自然语言，或粘贴已解析的用户画像 JSON",
            height=180,
        )
        if st.button("解析并填入", key="match_profile_button"):
            if not match_user_text.strip():
                st.warning("请先输入用户画像")
            else:
                try:
                    parsed = json.loads(match_user_text)
                    if not isinstance(parsed, dict):
                        raise ValueError
                    st.session_state["match_user_profile"] = parsed
                except (json.JSONDecodeError, ValueError):
                    with st.spinner("AI正在解析中..."):
                        data = call_api("/api/parse_profile", {"raw_text": match_user_text})
                    if data:
                        st.session_state["match_user_profile"] = data

        user_profile = st.session_state.get("match_user_profile")
        if user_profile:
            show_tags("技能标签", user_profile.get("skills", []))
            st.json(user_profile)

    with project_column:
        st.subheader("项目需求")
        match_project_text = st.text_area(
            "项目自然语言",
            placeholder="输入项目背景、所需技能、时间要求和项目类型",
            height=180,
        )
        if st.button("解析并填入", key="match_project_button"):
            if not match_project_text.strip():
                st.warning("请先输入项目需求")
            else:
                with st.spinner("AI正在解析中..."):
                    data = call_api("/api/parse_project", {"raw_text": match_project_text})
                if data:
                    st.session_state["match_project_profile"] = data

        project_profile = st.session_state.get("match_project_profile")
        if project_profile:
            show_tags("需求标签", project_profile.get("required_skills", []))
            st.json(project_profile)

    st.divider()
    if st.button("计算匹配度", type="primary", use_container_width=True):
        user_profile = st.session_state.get("match_user_profile")
        project_profile = st.session_state.get("match_project_profile")
        if not user_profile or not project_profile:
            st.warning("请先完成用户画像和项目需求解析")
        else:
            with st.spinner("正在计算匹配度..."):
                result = call_api(
                    "/api/match",
                    {"user_profile": user_profile, "project_profile": project_profile},
                )
            if result:
                st.session_state["match_result"] = result

    match_result = st.session_state.get("match_result")
    if match_result:
        st.subheader("匹配结果")
        st.metric("综合匹配度", f"{match_result.get('total_score', 0) * 100:.1f}%")

        skill_score = float(match_result.get("skill_match", 0))
        time_score = float(match_result.get("time_match", 0))
        experience_score = float(match_result.get("experience_match", 0))

        st.write(f"技能匹配：{skill_score * 100:.1f}%")
        st.progress(min(max(skill_score, 0.0), 1.0))
        st.write(f"时间匹配：{time_score * 100:.1f}%")
        st.progress(min(max(time_score, 0.0), 1.0))
        st.write(f"经历匹配：{experience_score * 100:.1f}%")
        st.progress(min(max(experience_score, 0.0), 1.0))
        st.info(match_result.get("explanation", "暂无匹配说明"))

st.caption("同校优先，跨校开放")
