import streamlit as st

from api_client import api_request
from ui import render_empty_state, render_page_intro


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

    result = api_request(
        "GET",
        path,
        token=token,
        params=params if search else None,
        success_message="用户列表加载成功",
    )
    if result is None:
        return None

    return [
        user for user in _extract_users(result)
        if user.get("role") == "user"
    ]


@st.dialog("封禁用户")
def _ban_user_dialog(user_id: int, username: str, token: str) -> None:
    st.write(f"确认封禁用户：{username}")
    reason = st.text_area(
        "封号原因（可空）",
        key=f"ban_reason_dialog_{user_id}",
        placeholder="请输入封号原因",
    )
    if st.button(
        "确认封号",
        key=f"confirm_ban_{user_id}",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("正在封禁用户..."):
            result = api_request(
                "POST",
                f"/api/admin/users/{user_id}/ban",
                token=token,
                json={"reason": reason.strip()},
                success_message="用户已封禁",
            )
        if result is not None:
            st.rerun()


@st.dialog("解封用户")
def _unban_user_dialog(user_id: int, username: str, token: str) -> None:
    st.write(f"确认解封用户：{username}")
    st.caption("解封不会自动恢复该用户已被下架的项目。")
    confirmed = st.checkbox(
        "我确认要解封该用户",
        key=f"unban_confirm_check_{user_id}",
    )
    if st.button(
        "确认解封",
        key=f"confirm_unban_{user_id}",
        type="primary",
        disabled=not confirmed,
        use_container_width=True,
    ):
        with st.spinner("正在解封用户..."):
            result = api_request(
                "POST",
                f"/api/admin/users/{user_id}/unban",
                token=token,
                success_message="用户已解封",
            )
        if result is not None:
            st.rerun()


# [TEST-ONLY] 硬删除用户，正式版需移除。
@st.dialog("删除用户")
def _delete_user_dialog(user_id: int, username: str, token: str) -> None:
    st.warning(f"此操作将永久删除用户及其项目数据：{username}")
    confirmation = st.text_input(
        "请输入该用户的 username 进行确认",
        key=f"delete_user_confirmation_{user_id}",
    )
    if st.button(
        "确认永久删除",
        key=f"confirm_delete_user_{user_id}",
        type="primary",
        use_container_width=True,
    ):
        if confirmation.strip() != username:
            st.error("用户名不一致，无法删除")
            return
        with st.spinner("正在永久删除用户..."):
            result = api_request(
                "DELETE",
                f"/api/admin/users/{user_id}",
                token=token,
                success_message="用户已删除",
            )
        if result is not None:
            st.rerun()


st.set_page_config(
    page_title="用户管理 - 知遇LinkLab",
    page_icon="👥",
    layout="wide",
)

render_page_intro("用户管理", "检索平台用户并查看学校、专业和账号信息。", eyebrow="平台运营")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

st.subheader("搜索用户")
col1, col2, col3 = st.columns(3)
with col1:
    username = st.text_input("用户名")
with col2:
    school = st.text_input("学校")
with col3:
    major = st.text_input("专业")

search_submitted = st.button("搜索", type="primary", icon=":material/search:")
if search_submitted:
    st.session_state["admin_user_search"] = {
        "username": username.strip(), "school": school.strip(), "major": major.strip(),
    }
search_params = st.session_state.get("admin_user_search")

with st.spinner("正在加载用户列表..."):
    if search_params is not None:
        users = _load_users(
            admin_token,
            search=True,
            params=search_params,
        )
    else:
        users = _load_users(admin_token)

if users is None:
    st.stop()

st.divider()
st.subheader("用户列表")
if users:
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] button {
            min-height: 2rem;
            padding: 0.2rem 0.55rem;
            font-size: 0.82rem;
        }
        button[aria-label="封号"] {
            background: #f79009 !important;
            border-color: #f79009 !important;
            color: white !important;
        }
        button[aria-label="解封"] {
            background: #12b76a !important;
            border-color: #12b76a !important;
            color: white !important;
        }
        button[aria-label="删除"],
        button[aria-label="确认永久删除"] {
            background: #d92d20 !important;
            border-color: #d92d20 !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    for index, user in enumerate(users):
        user_id = user.get("id") or user.get("user_id")
        user_name = str(user.get("username") or "未命名用户")
        is_banned = bool(user.get("is_banned"))
        with st.container(border=True):
            info_col, status_col, action_col, delete_col = st.columns(
                [3.8, 1.4, 1.25, 1.25],
                vertical_alignment="center",
            )
            with info_col:
                st.markdown(f"**{user_name}**")
                st.caption(
                    f"{user.get('email') or '未填写邮箱'} · "
                    f"{user.get('school') or '未填写学校'} · "
                    f"{user.get('major') or '未填写专业'}"
                )
            with status_col:
                if is_banned:
                    reason = user.get("ban_reason") or "未填写原因"
                    st.markdown(
                        f'<span title="{reason}" style="color:#b42318;'
                        'font-weight:600;">● 已封禁</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("正常")
            with action_col:
                if user_id is None:
                    st.button(
                        "封号",
                        key=f"ban_missing_id_{index}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif is_banned:
                    if st.button(
                        "解封",
                        key=f"unban_user_{user_id}",
                        use_container_width=True,
                    ):
                        _unban_user_dialog(user_id, user_name, admin_token)
                elif st.button(
                    "封号",
                    key=f"ban_user_{user_id}",
                    use_container_width=True,
                ):
                    _ban_user_dialog(user_id, user_name, admin_token)
            with delete_col:
                # [TEST-ONLY] 硬删除用户，正式版需移除。
                if user_id is None:
                    st.button(
                        "删除",
                        key=f"delete_missing_id_{index}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif st.button(
                    "删除",
                    key=f"delete_user_{user_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    _delete_user_dialog(user_id, user_name, admin_token)
else:
    render_empty_state("没有符合条件的用户", "请调整搜索条件后重试。", icon="person_search")

st.page_link("admin_dashboard.py", label="返回管理员首页", icon=":material/arrow_back:")
