import streamlit as st

from api_client import api_request
from ui import render_empty_state, render_page_intro


def _extract_users(result: object) -> list[dict]:
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]

    if not isinstance(result, dict):
        return []

    for key in ("data", "users", "items", "results"):
        value = result.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def _load_users(
    token: str,
    search: bool = False,
    params: dict[str, str] | None = None,
) -> list[dict] | None:
    path = "/api/admin/users/search" if search else "/api/admin/users"

    result = api_request(
        "GET",
        path,
        token=token,
        params=params if search else None,
        success_message="用户列表加载成功",
    )
    if result is None:
        return None

    return _extract_users(result)


st.set_page_config(
    page_title="用户管理 - 知遇LinkLab",
    page_icon="👥",
    layout="wide",
)

render_page_intro("用户管理", "检索平台用户并查看学校、专业和账号信息。", eyebrow="平台运营")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

st.subheader("搜索用户")
col1, col2, col3 = st.columns(3)
with col1:
    username = st.text_input("用户名")
with col2:
    school = st.text_input("学校")
with col3:
    major = st.text_input("专业")

search_submitted = st.button("搜索", type="primary", icon=":material/search:")
if search_submitted:
    st.session_state["admin_user_search"] = {
        "username": username.strip(), "school": school.strip(), "major": major.strip(),
    }
search_params = st.session_state.get("admin_user_search")

with st.spinner("正在加载用户列表..."):
    if search_params is not None:
        users = _load_users(
            admin_token,
            search=True,
            params=search_params,
        )
    else:
        users = _load_users(admin_token)

if users is None:
    st.stop()

st.divider()
st.subheader("用户列表")
if users:
    st.dataframe(
        users,
        column_config={"username": "用户名", "school": "学校", "major": "专业"},
        use_container_width=True,
        hide_index=True,
    )
else:
    render_empty_state("没有符合条件的用户", "请调整搜索条件后重试。", icon="person_search")

st.page_link("admin_dashboard.py", label="返回管理员首页", icon=":material/arrow_back:")
