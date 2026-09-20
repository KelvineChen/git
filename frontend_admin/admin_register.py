import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"

REGISTER_ERROR_MESSAGES = {
    "admin_name_exists": "管理员名称已存在",
    "invalid_admin_name": "管理员名称不合法",
}


st.set_page_config(
    page_title="管理员注册 - 知遇LinkLab",
    page_icon="📝",
    layout="centered",
)

st.title("管理员注册申请")
st.caption("提交后等待管理员审核")

with st.form("admin_register_form"):
    admin_name = st.text_input("admin_name")
    user_password = st.text_input(
        "user_password",
        type="password",
        help="管理员操作用户数据时使用的用户密码",
    )
    submitted = st.form_submit_button(
        "注册",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not admin_name.strip() or not user_password:
        st.warning("请填写完整的注册信息")
    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/admin/register",
                json={
                    "admin_name": admin_name.strip(),
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
                REGISTER_ERROR_MESSAGES.get(
                    error_code,
                    error_code or "管理员注册失败",
                )
            )
        except requests.RequestException:
            st.error("注册服务暂不可用，请稍后重试")
        except ValueError:
            st.error("注册服务返回的数据格式不正确")
        else:
            if result.get("error"):
                error_code = result["error"]
                st.error(
                    REGISTER_ERROR_MESSAGES.get(
                        error_code,
                        error_code,
                    )
                )
            else:
                st.success("注册成功，等待管理员审核")

st.divider()
st.page_link("admin_login.py", label="返回管理员登录")
