import streamlit as st

from api_client import api_request

REGISTER_ERROR_MESSAGES = {
    "admin_name_exists": "管理员名称已存在",
    "invalid_admin_name": "管理员名称不合法",
    "password_mismatch": "两次输入的管理员密码不一致",
    "password_too_short": "两类密码都至少需要8位",
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
    admin_password = st.text_input("admin_password", type="password")
    confirm_admin_password = st.text_input(
        "confirm_admin_password", type="password"
    )
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
    if not all(
        [admin_name.strip(), admin_password, confirm_admin_password, user_password]
    ):
        st.warning("请填写完整的注册信息")
    elif admin_password != confirm_admin_password:
        st.error("两次输入的管理员密码不一致")
    else:
        with st.spinner("正在提交管理员申请..."):
            api_request(
                "POST",
                "/api/admin/register",
                json={
                    "admin_name": admin_name.strip(),
                    "admin_password": admin_password,
                    "confirm_admin_password": confirm_admin_password,
                    "user_password": user_password,
                },
                success_message="注册成功，等待管理员审核",
                error_messages=REGISTER_ERROR_MESSAGES,
            )

st.divider()
st.page_link("admin_login.py", label="返回管理员登录")
