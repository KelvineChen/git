import streamlit as st

from ui import inject_theme, render_brand_lockup


st.set_page_config(
    page_title="知遇LinkLab 管理员系统",
    page_icon="🛠️",
    layout="wide",
)

inject_theme("admin" if st.session_state.get("admin_token") else "auth")

with st.sidebar:
    render_brand_lockup(
        compact=True,
        inverse=True,
        subtitle="平台运营与内容治理",
    )


if st.session_state.get("admin_token"):
    # Keep auth pages registered but hidden so a login redirect can resolve
    # after the session state changes without a PageNotFoundError.
    pages = [
        st.Page(
            "admin_login.py",
            title="管理员登录",
            icon=":material/login:",
            visibility="hidden",
        ),
        st.Page(
            "admin_register.py",
            title="管理员注册",
            icon=":material/person_add:",
            visibility="hidden",
        ),
        st.Page(
            "admin_dashboard.py",
            title="管理员控制台",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "admin_users.py",
            title="用户管理",
            icon=":material/group:",
        ),
        st.Page(
            "admin_competitions.py",
            title="项目招募管理",
            icon=":material/emoji_events:",
        ),
        st.Page(
            "admin_review.py",
            title="管理员审核",
            icon=":material/rate_review:",
        ),
        st.Page(
            "admin_feedback.py",
            title="反馈处理",
            icon=":material/feedback:",
        ),
    ]
else:
    pages = [
        st.Page(
            "admin_login.py",
            title="管理员登录",
            icon=":material/login:",
            default=True,
        ),
        st.Page(
            "admin_register.py",
            title="管理员注册",
            icon=":material/person_add:",
        ),
    ]

pg = st.navigation(pages)

if st.session_state.get("admin_token"):
    with st.sidebar:
        st.caption(f"当前管理员：{st.session_state.get('admin_name', '未知')}")
        if st.button(
            "退出管理端",
            key="logout_button",
            icon=":material/logout:",
            use_container_width=True,
        ):
            st.session_state.clear()
            st.rerun()
pg.run()
