import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"

LOGIN_ERROR_MESSAGES = {
    "admin_not_found": "管理员不存在",
    "invalid_admin_password": "管理员密码错误",
    "invalid_user_password": "用户密码错误",
    "admin_not_approved": "管理员未审核",
}


st.set_page_config(
    page_title="管理员登录 - 知遇LinkLab",
    page_icon="🔐",
    layout="centered",
)

st.title("知遇LinkLab 管理员登录")
st.caption("管理员后台入口")

if st.session_state.get("admin_token"):
    st.switch_page("admin_dashboard.py")

with st.form("admin_login_form"):
    admin_name = st.text_input("admin_name")
    admin_password = st.text_input(
        "admin_password",
        type="password",
    )
    user_password = st.text_input(
        "user_password",
        type="password",
    )
    submitted = st.form_submit_button(
        "登录",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not admin_name.strip() or not admin_password or not user_password:
        st.warning("请填写完整的登录信息")
    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/admin/login",
                json={
                    "admin_name": admin_name.strip(),
                    "admin_password": admin_password,
                    "user_password": user_password,
                },
                timeout=15,
            )
            response.raise_for_status()
            result = response.json()
        except requests.HTTPError as error:
            try:
                error_code = error.response.json().get("error")
            except (AttributeError, ValueError):
                error_code = None

            st.error(
                LOGIN_ERROR_MESSAGES.get(
                    error_code,
                    "管理员登录失败，请稍后重试",
                )
            )
        except requests.RequestException:
            st.error("登录服务暂不可用，请稍后重试")
        except ValueError:
            st.error("登录服务返回的数据格式不正确")
        else:
            token = result.get("token")
            if not token:
                error_code = result.get("error")
                st.error(
                    LOGIN_ERROR_MESSAGES.get(
                        error_code,
                        "管理员登录失败，请稍后重试",
                    )
                )
            else:
                st.session_state["admin_token"] = token
                st.session_state["admin_name"] = admin_name.strip()
                admin_status = result.get("admin_status")
                if admin_status is None:
                    st.session_state.pop("admin_status", None)
                else:
                    st.session_state["admin_status"] = admin_status
                # Rerun so admin_app.py registers dashboard before switching.
                st.rerun()

st.divider()
st.page_link("admin_register.py", label="申请注册管理员")
