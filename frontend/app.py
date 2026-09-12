import requests
import streamlit as st


BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="知遇LinkLab - 找到你的科研搭档")
st.title("知遇LinkLab - 找到你的科研搭档")

try:
    health_response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    health_response.raise_for_status()
    st.success("后端连接正常")
except requests.RequestException:
    st.error("后端未启动，请先启动后端服务")

st.header("输入区")
raw_text = st.text_area(
    "用户描述",
    placeholder="请用自然语言描述你的技能、经历和协作偏好",
    height=180,
)

if st.button("解析"):
    if not raw_text.strip():
        st.warning("请先输入你的技能、经历和协作偏好")
    else:
        with st.spinner("AI正在解析中..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/parse_profile",
                    json={"raw_text": raw_text},
                    timeout=60,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("success"):
                    st.session_state["profile_result"] = result.get("data", {})
                    st.session_state.pop("profile_error", None)
                else:
                    st.session_state.pop("profile_result", None)
                    st.session_state["profile_error"] = result.get(
                        "message", "解析失败，请重试"
                    )
            except (requests.RequestException, ValueError):
                st.session_state.pop("profile_result", None)
                st.session_state["profile_error"] = "解析失败，请重试"

st.header("结果展示区")

if st.session_state.get("profile_error"):
    st.error(st.session_state["profile_error"])

profile = st.session_state.get("profile_result")
if profile:
    skills = profile.get("skills", [])
    if skills:
        st.markdown("**技能标签**")
        st.markdown(" ".join(f"`{skill}`" for skill in skills))

    skill_levels = profile.get("skill_levels", {})
    if skill_levels:
        st.subheader("技能等级")
        for skill, level in skill_levels.items():
            st.markdown(f"- **{skill}**：{level}")

    experience = profile.get("experience", [])
    if experience:
        st.subheader("项目经历")
        for item in experience:
            st.markdown(f"- {item}")

    interests = profile.get("interests", [])
    if interests:
        st.subheader("兴趣方向")
        for item in interests:
            st.markdown(f"- {item}")

    st.subheader("协作偏好")
    st.write(profile.get("preference", "未提供"))

    st.subheader("时间投入")
    st.write(profile.get("time_commitment", "未提供"))

st.markdown(
    "<div style='position: fixed; bottom: 20px; width: 100%; text-align: center;'>"
    "同校优先，跨校开放"
    "</div>",
    unsafe_allow_html=True,
)
