import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"


def _error_code(response: requests.Response) -> str:
    try:
        return response.json().get("error", "request_failed")
    except ValueError:
        return "request_failed"


def _extract_admins(result: object) -> list[dict]:
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]

    if not isinstance(result, dict):
        return []

    for key in ("data", "admins", "items", "results"):
        value = result.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def _load_pending_admins(token: str) -> list[dict] | None:
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/admin/review/list",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(f"加载审核列表失败：{_error_code(error.response)}")
        else:
            st.error("加载审核列表失败")
        return None
    except requests.RequestException:
        st.error("审核服务暂不可用，请稍后重试")
        return None
    except ValueError:
        st.error("审核服务返回的数据格式不正确")
        return None

    admins = _extract_admins(result)
    return [
        admin
        for admin in admins
        if admin.get("admin_status", admin.get("status", "pending"))
        == "pending"
    ]


def _review_admin(token: str, admin_name: str, action: str) -> bool:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/admin/review/action",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "admin_name": admin_name,
                "action": action,
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(f"审核操作失败：{_error_code(error.response)}")
        else:
            st.error("审核操作失败")
        return False
    except requests.RequestException:
        st.error("审核服务暂不可用，请稍后重试")
        return False

    return True


st.set_page_config(
    page_title="管理员审核 - 知遇LinkLab",
    page_icon="✅",
    layout="wide",
)

st.title("管理员审核")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

if st.session_state.get("admin_status") != "approved":
    st.error("当前管理员未审核通过，禁止访问此页面")
    st.stop()

st.caption("仅显示 admin_status = pending 的管理员")

pending_admins = _load_pending_admins(admin_token)
if pending_admins is None:
    st.stop()

if not pending_admins:
    st.info("暂无待审核管理员")
else:
    for index, admin in enumerate(pending_admins):
        admin_name = str(admin.get("admin_name", "未提供"))
        username = str(admin.get("username") or "未关联")
        created_at = str(admin.get("created_at") or "未提供")
        status = str(admin.get("admin_status", admin.get("status", "pending")))

        with st.container(border=True):
            info_col, action_col = st.columns([4, 2])
            with info_col:
                st.write(f"**admin_name：**{admin_name}")
                st.write(f"**username：**{username}")
                st.write(f"**created_at：**{created_at}")
                st.write(f"**状态：**{status}")

            with action_col:
                if st.button(
                    "通过",
                    key=f"approve_{index}_{admin_name}",
                    use_container_width=True,
                ):
                    if _review_admin(admin_token, admin_name, "approve"):
                        st.rerun()

                if st.button(
                    "拒绝",
                    key=f"reject_{index}_{admin_name}",
                    use_container_width=True,
                ):
                    if _review_admin(admin_token, admin_name, "reject"):
                        st.rerun()

st.divider()
st.page_link("admin_dashboard.py", label="返回管理员首页")
