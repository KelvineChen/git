import streamlit as st

from api_client import api_request


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
        success_message="竞赛列表加载成功",
    )
    if result is None:
        return None

    return _extract_competitions(result)


st.set_page_config(
    page_title="竞赛招募管理 - 知遇LinkLab",
    page_icon="🏆",
    layout="wide",
)

st.title("竞赛招募管理")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.page_link("admin_login.py", label="前往管理员登录")
    st.stop()

st.subheader("搜索竞赛")
col1, col2 = st.columns(2)
with col1:
    title = st.text_input("title")
with col2:
    creator = st.text_input("creator")

search_submitted = st.button("搜索", type="primary")

with st.spinner("正在加载竞赛列表..."):
    if search_submitted:
        competitions = _load_competitions(
            admin_token,
            search=True,
            params={"title": title.strip(), "creator": creator.strip()},
        )
    else:
        competitions = _load_competitions(admin_token)

if competitions is None:
    st.stop()

st.divider()
st.subheader("竞赛列表")
st.dataframe(
    competitions,
    column_config={
        "title": "竞赛名称",
        "creator": "发布者名称",
        "status": "状态",
        "created_at": "创建时间",
    },
    use_container_width=True,
    hide_index=True,
)

st.page_link("admin_dashboard.py", label="返回管理员首页")
