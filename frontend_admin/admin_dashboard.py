import streamlit as st


st.set_page_config(
    page_title="管理员控制台 - 知遇LinkLab",
    page_icon="🛠️",
    layout="wide",
)

st.title("管理员控制台")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

admin_name = st.session_state.get("admin_name", "未知管理员")
admin_status = st.session_state.get("admin_status", "unknown")

st.success(f"欢迎你，管理员 {admin_name}")
st.write(f"管理员状态：{admin_status}")

st.subheader("管理功能")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("用户管理", use_container_width=True):
        st.switch_page("admin_users.py")
with col2:
    if st.button("竞赛招募管理", use_container_width=True):
        st.switch_page("admin_competitions.py")
with col3:
    if st.button("管理员审核", use_container_width=True):
        st.switch_page("admin_review.py")
