import streamlit as st

from api_client import api_request
from ui import render_brand_lockup

LOGIN_ERROR_MESSAGES = {
    "admin_not_found": "管理员不存在",
    "invalid_admin_password": "管理员密码错误",
    "invalid_user_password": "用户操作密码错误",
    "admin_not_approved": "管理员账号尚未通过审核",
}


st.set_page_config(
    page_title="管理员登录 - 知遇LinkLab",
    page_icon="🔐",
    layout="wide",
)

if st.session_state.get("admin_token"):
    st.switch_page("admin_dashboard.py")

copy_column, form_column = st.columns([1.15, 0.85], gap="large")
with copy_column:
    with st.container(key="auth_copy"):
        render_brand_lockup(inverse=True, subtitle="平台运营与内容治理")
        st.markdown(
            """
            <div class="zl-auth-kicker">PLATFORM OPERATIONS</div>
            <h1>知遇 LinkLab 管理后台</h1>
            <p>统筹平台运营，规范内容治理，守护科研协作秩序。</p>
            <div class="zl-auth-proof"><span>运营统计</span><span>内容治理</span><span>权限审核</span></div>
            """,
            unsafe_allow_html=True,
        )

with form_column:
    with st.container(key="auth_panel"):
        st.markdown(
            '<div class="zl-auth-panel-head"><h2>管理员登录</h2>'
            '<p>请使用已通过审核的管理员账号登录</p></div>',
            unsafe_allow_html=True,
        )
        with st.form("admin_login_form"):
            admin_name = st.text_input("管理员名称")
            admin_password = st.text_input("管理员密码", type="password")
            user_password = st.text_input("用户操作密码", type="password")
            submitted = st.form_submit_button(
                "进入管理端",
                type="primary",
                icon=":material/admin_panel_settings:",
                use_container_width=True,
            )
        st.page_link(
            "admin_register.py",
            label="申请注册管理员",
            icon=":material/person_add:",
        )

if submitted:
    if not admin_name.strip() or not admin_password or not user_password:
        st.warning("请填写完整的登录信息")
    else:
        with st.spinner("正在登录..."):
            result = api_request(
                "POST",
                "/api/admin/login",
                json={
                    "admin_name": admin_name.strip(),
                    "admin_password": admin_password,
                    "user_password": user_password,
                },
                success_message="管理员登录成功",
                error_messages=LOGIN_ERROR_MESSAGES,
            )
        if result:
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
