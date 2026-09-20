import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"


def _error_code(response: requests.Response) -> str:
    try:
        return response.json().get("error", "request_failed")
    except ValueError:
        return "request_failed"


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

    try:
        response = requests.get(
            f"{BACKEND_URL}{path}",
            headers={"Authorization": f"Bearer {token}"},
            params=params if search else None,
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(_error_code(error.response))
        else:
            st.error("用户列表请求失败")
        return None
    except requests.RequestException:
        st.error("用户管理服务暂不可用，请稍后重试")
        return None
    except ValueError:
        st.error("用户管理服务返回的数据格式不正确")
        return None

    if isinstance(result, dict) and result.get("error"):
        st.error(str(result["error"]))
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
