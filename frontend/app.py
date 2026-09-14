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

profile_tab, project_tab = st.tabs(["能力画像", "项目发布"])

with profile_tab:
    st.header("输入区")
    raw_text = st.text_area("用户描述", placeholder="请用自然语言描述你的技能、经历和协作偏好", height=180)
    if st.button("解析", key="profile_button"):
        with st.spinner("AI正在解析中..."):
            try:
                result = requests.post(f"{BACKEND_URL}/api/parse_profile", json={"raw_text": raw_text}, timeout=60).json()
                if result.get("success"):
                    st.json(result["data"])
                else:
                    st.error(result.get("message", "解析失败，请重试"))
            except (requests.RequestException, ValueError):
                st.error("解析失败，请重试")

with project_tab:
    st.header("项目发布")
    project_name = st.text_input("项目名称")
    project_text = st.text_area("需求描述", placeholder="请描述项目背景、所需技能、时间要求和优先条件")
    if st.button("解析", key="project_button"):
        if not project_name.strip() or not project_text.strip():
            st.warning("请填写项目名称和需求描述")
        else:
            with st.spinner("AI正在解析中..."):
                try:
                    result = requests.post(f"{BACKEND_URL}/api/parse_project", json={"raw_text": project_text}, timeout=60).json()
                    if result.get("success"):
                        st.subheader("解析结果")
                        st.json(result["data"])
                    else:
                        st.error(result.get("message", "解析失败，请重试"))
                except (requests.RequestException, ValueError):
                    st.error("解析失败，请重试")

    st.header("结果展示区")

st.markdown(
    "<div style='position: fixed; bottom: 20px; width: 100%; text-align: center;'>"
    "同校优先，跨校开放"
    "</div>",
    unsafe_allow_html=True,
)
