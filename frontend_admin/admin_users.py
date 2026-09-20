import streamlit as st

from api_client import api_request


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

st.title("用户管理")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

st.subheader("搜索用户")
col1, col2, col3 = st.columns(3)
with col1:
    username = st.text_input("username")
with col2:
    school = st.text_input("school")
with col3:
    major = st.text_input("major")

search_submitted = st.button("搜索", type="primary")

with st.spinner("正在加载用户列表..."):
    if search_submitted:
        users = _load_users(
            admin_token,
            search=True,
            params={
                "username": username.strip(),
                "school": school.strip(),
                "major": major.strip(),
            },
        )
    else:
        users = _load_users(admin_token)

if users is None:
    st.stop()

st.divider()
st.subheader("用户列表")
st.dataframe(
    users,
    column_config={
        "username": "username",
        "school": "school",
        "major": "major",
    },
    use_container_width=True,
    hide_index=True,
)

st.page_link("admin_dashboard.py", label="返回管理员首页")
