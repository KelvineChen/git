import streamlit as st


st.set_page_config(
    page_title="知遇LinkLab 管理员系统",
    page_icon="🛠️",
    layout="wide",
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
            title="竞赛招募管理",
            icon=":material/emoji_events:",
        ),
        st.Page(
            "admin_review.py",
            title="管理员审核",
            icon=":material/rate_review:",
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
pg.run()
