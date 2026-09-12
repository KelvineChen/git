import requests
import streamlit as st


st.set_page_config(page_title="知遇LinkLab - 找到你的科研搭档")

st.title("知遇LinkLab - 找到你的科研搭档")

st.markdown(
    "<div style='text-align: center; margin-top: 30vh;'>"
    "<h2>欢迎来到知遇LinkLab</h2>"
    "</div>",
    unsafe_allow_html=True,
)

try:
    response = requests.get("http://localhost:8000/api/health", timeout=5)
    response.raise_for_status()
    st.success("后端连接正常")
except requests.RequestException:
    st.error("后端未启动，请先启动后端服务")

st.markdown(
    "<div style='position: fixed; bottom: 20px; width: 100%; text-align: center;'>"
    "同校优先，跨校开放"
    "</div>",
    unsafe_allow_html=True,
)