import streamlit as st

from api_client import api_request
from ui import render_brand_lockup

REGISTER_ERROR_MESSAGES = {
    "admin_name_exists": "管理员名称已存在",
    "invalid_admin_name": "管理员名称不合法",
    "password_mismatch": "两次输入的管理员密码不一致",
    "password_too_short": "管理员密码和用户操作密码均须至少8位",
}


st.set_page_config(
    page_title="管理员注册 - 知遇LinkLab",
    page_icon="📝",
    layout="wide",
)

copy_column, form_column = st.columns([1.05, 0.95], gap="large")
with copy_column:
    with st.container(key="auth_copy"):
        render_brand_lockup(inverse=True, subtitle="平台运营与内容治理")
        st.markdown(
            """
            <div class="zl-auth-kicker">ADMIN ACCESS</div>
            <h1>申请平台管理权限</h1>
            <p>注册申请经审核通过后，方可使用管理功能。</p>
            """,
            unsafe_allow_html=True,
        )

with form_column:
    with st.container(key="auth_panel"):
        st.markdown(
            '<div class="zl-auth-panel-head"><h2>管理员注册</h2>'
            '<p>请设置管理员账号与操作密码</p></div>',
            unsafe_allow_html=True,
        )
        with st.form("admin_register_form"):
            admin_name = st.text_input("管理员名称")
            password_left, password_right = st.columns(2)
            with password_left:
                admin_password = st.text_input("管理员密码", type="password")
            with password_right:
                confirm_admin_password = st.text_input("确认管理员密码", type="password")
            user_password = st.text_input(
                "用户操作密码",
                type="password",
                help="用于管理员操作用户数据时的身份验证，并非普通用户的登录密码",
            )
            submitted = st.form_submit_button(
                "提交注册申请",
                type="primary",
                icon=":material/send:",
                use_container_width=True,
            )
        st.page_link(
            "admin_login.py",
            label="返回管理员登录",
            icon=":material/arrow_back:",
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
                success_message="注册申请已提交，请等待审核",
                error_messages=REGISTER_ERROR_MESSAGES,
            )
