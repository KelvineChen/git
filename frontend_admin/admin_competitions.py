import streamlit as st

from api_client import api_request
from ui import render_empty_state, render_page_intro


def _extract_competitions(result: object) -> list[dict]:
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]

    if not isinstance(result, dict):
        return []

    for key in ("data", "competitions", "items", "results"):
        value = result.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def _load_competitions(
    token: str,
    search: bool = False,
    params: dict[str, str] | None = None,
) -> list[dict] | None:
    path = (
        "/api/admin/competitions/search"
        if search
        else "/api/admin/competitions"
    )

    result = api_request(
        "GET",
        path,
        token=token,
        params=params if search else None,
        success_message="项目列表加载成功",
    )
    if result is None:
        return None

    return _extract_competitions(result)


@st.dialog("删除项目")
def _delete_project_dialog(
    project_id: int,
    title: str,
    token: str,
) -> None:
    st.warning(f"此操作将永久删除项目及其关联数据：{title}")
    confirmation = st.text_input(
        "请输入项目名称进行确认",
        key=f"delete_competition_confirmation_{project_id}",
    )
    if st.button(
        "确认永久删除",
        key=f"confirm_delete_competition_{project_id}",
        type="primary",
        use_container_width=True,
    ):
        if confirmation.strip() != title:
            st.error("项目名称不一致，无法删除")
            return
        with st.spinner("正在永久删除项目..."):
            result = api_request(
                "DELETE",
                f"/api/admin/competitions/{project_id}",
                token=token,
                success_message="项目已删除",
                error_messages={
                    "project_not_found": "项目不存在或已被删除",
                },
            )
        if result is not None:
            st.rerun()


st.set_page_config(
    page_title="项目招募管理 - 知遇LinkLab",
    page_icon="🏆",
    layout="wide",
)

st.markdown(
    """
    <style>
    div[data-testid="stButton"] button {
        min-height: 2rem;
        padding: 0.2rem 0.6rem;
        font-size: 0.82rem;
    }
    button[aria-label="删除项目"],
    button[aria-label="确认永久删除"] {
        background: #d92d20 !important;
        border-color: #d92d20 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_page_intro("项目招募管理", "搜索平台项目，检查内容并执行下架或恢复操作。", eyebrow="内容治理")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

st.subheader("搜索项目")
col1, col2 = st.columns(2)
with col1:
    title = st.text_input("项目名称")
with col2:
    creator = st.text_input("发布者")

search_submitted = st.button("搜索", type="primary", icon=":material/search:")
if search_submitted:
    st.session_state["admin_project_search"] = {"title": title.strip(), "creator": creator.strip()}
search_params = st.session_state.get("admin_project_search")

with st.spinner("正在加载项目列表..."):
    if search_params is not None:
        competitions = _load_competitions(
            admin_token,
            search=True,
            params=search_params,
        )
    else:
        competitions = _load_competitions(admin_token)

if competitions is None:
    st.stop()

st.divider()
st.subheader("项目内容治理")
status_labels = {
    "recruiting": "招募中",
    "full": "已满员",
    "closed": "已关闭",
    "completed": "已完成",
}
moderation_labels = {"active": "正常展示", "removed": "平台已下架"}

if not competitions:
    render_empty_state("当前没有项目", "平台暂时没有符合条件的项目记录。", icon="science")

for project in competitions:
    project_id = project.get("id")
    moderation_status = project.get("moderation_status", "active")
    with st.expander(
        f"#{project_id} · {project.get('title') or '未命名项目'} · "
        f"{moderation_labels.get(moderation_status, moderation_status)}"
    ):
        metrics = st.columns(3)
        metrics[0].metric("发布者", project.get("creator") or "未填写")
        metrics[1].metric(
            "业务状态",
            status_labels.get(project.get("status"), project.get("status") or "未知"),
        )
        metrics[2].metric(
            "治理状态",
            moderation_labels.get(moderation_status, moderation_status),
        )
        st.write(project.get("description") or "暂无项目描述")
        st.caption(f"发布时间：{str(project.get('created_at') or '')[:16]}")
        if project.get("moderation_reason"):
            st.warning(f"最近处理原因：{project['moderation_reason']}")

        if moderation_status == "removed":
            restore_reason = st.text_input(
                "恢复说明（可选）",
                key=f"restore_reason_{project_id}",
            )
            if st.button(
                "恢复项目展示",
                key=f"restore_project_{project_id}",
                type="primary",
                icon=":material/restore:",
            ):
                with st.spinner("正在恢复项目..."):
                    saved = api_request(
                        "POST",
                        f"/api/admin/project/{project_id}/moderation",
                        token=admin_token,
                        json={"action": "restore", "reason": restore_reason},
                        success_message="项目已恢复展示",
                    )
                if saved is not None:
                    st.rerun()
        else:
            reason = st.text_area(
                "下架原因",
                placeholder="请说明违规内容或需要整改的问题",
                key=f"remove_reason_{project_id}",
            )
            if st.button(
                "下架项目",
                key=f"danger_remove_project_{project_id}",
                icon=":material/block:",
            ):
                if not reason.strip():
                    st.error("请先填写下架原因")
                else:
                    with st.spinner("正在下架项目..."):
                        saved = api_request(
                            "POST",
                            f"/api/admin/project/{project_id}/moderation",
                            token=admin_token,
                            json={"action": "remove", "reason": reason},
                            success_message="项目已下架",
                        )
                    if saved is not None:
                        st.rerun()

        if st.button(
            "删除项目",
            key=f"delete_competition_{project_id}",
            type="primary",
            use_container_width=True,
        ):
            _delete_project_dialog(
                project_id,
                str(project.get("title") or "未命名项目"),
                admin_token,
            )

st.page_link("admin_dashboard.py", label="返回管理员首页", icon=":material/arrow_back:")
