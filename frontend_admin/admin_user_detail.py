import streamlit as st

from api_client import api_request
KNOWN_FIELDS = (
    ("username", "用户名"),
    ("email", "邮箱"),
    ("school", "学校"),
    ("major", "专业"),
    ("grade", "年级"),
    ("role", "角色"),
    ("created_at", "创建时间"),
)
SENSITIVE_FIELDS = {
    "password_hash",
    "user_password_hash",
    "admin_password_hash",
}


def _query_username() -> str:
    try:
        query_params = st.experimental_get_query_params()
        values = query_params.get("username", [])
        if isinstance(values, list):
            return str(values[0]).strip() if values else ""
        return str(values).strip()
    except AttributeError:
        value = st.query_params.get("username", "")
        return str(value).strip()


def _load_user_detail(token: str, username: str) -> dict | None:
    result = api_request(
        "GET",
        f"/api/admin/user/{username}",
        token=token,
        success_message="用户详情加载成功",
    )
    if result is None:
        return None

    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        return result["data"]
    if isinstance(result, dict):
        return result

    st.error("用户详情数据格式不正确")
    return None


st.set_page_config(
    page_title="用户详情 - 知遇LinkLab",
    page_icon="👤",
    layout="wide",
)

st.title("用户详情")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

username = _query_username()
if not username:
    st.error("缺少 username URL 参数")
    if st.button("返回用户管理页面"):
        st.switch_page("admin_users.py")
    st.stop()

with st.spinner("正在加载用户详情..."):
    user_data = _load_user_detail(admin_token, username)
if user_data is not None:
    displayed_fields = set()

    for field, label in KNOWN_FIELDS:
        st.write(f"{label}：", user_data.get(field, "未提供"))
        displayed_fields.add(field)

    extra_fields = {
        key: value
        for key, value in user_data.items()
        if key not in displayed_fields and key not in SENSITIVE_FIELDS
    }
    for field, value in extra_fields.items():
        st.write(f"{field}：", value)

st.divider()
if st.button("返回用户管理页面"):
    st.switch_page("admin_users.py")
