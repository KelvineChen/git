import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"
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


def _error_code(response: requests.Response) -> str:
    try:
        return response.json().get("error", "request_failed")
    except ValueError:
        return "request_failed"


def _load_user_detail(token: str, username: str) -> dict | None:
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/admin/user/{username}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(_error_code(error.response))
        else:
            st.error("用户详情请求失败")
        return None
    except requests.RequestException:
        st.error("用户详情服务暂不可用，请稍后重试")
        return None
    except ValueError:
        st.error("用户详情服务返回的数据格式不正确")
        return None

    if isinstance(result, dict) and result.get("error"):
        st.error(str(result["error"]))
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
