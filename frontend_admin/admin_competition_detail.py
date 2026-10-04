import streamlit as st

from api_client import api_request
from ui import render_page_intro
KNOWN_FIELDS = (
    ("title", "竞赛名称"),
    ("creator", "发布者"),
    ("description", "描述"),
    ("created_at", "发布时间"),
)


def _query_competition_id() -> str:
    try:
        query_params = st.experimental_get_query_params()
        values = query_params.get("competition_id", [])
        if isinstance(values, list):
            return str(values[0]).strip() if values else ""
        return str(values).strip()
    except AttributeError:
        value = st.query_params.get("competition_id", "")
        return str(value).strip()


def _load_competition_detail(
    token: str,
    competition_id: str,
) -> dict | None:
    result = api_request(
        "GET",
        f"/api/admin/competition/{competition_id}",
        token=token,
        success_message="竞赛详情加载成功",
    )
    if result is None:
        return None

    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        return result["data"]
    if isinstance(result, dict):
        return result

    st.error("竞赛详情数据格式不正确")
    return None


st.set_page_config(
    page_title="竞赛详情 - 知遇LinkLab",
    page_icon="🏆",
    layout="wide",
)

render_page_intro("项目详情", "查看项目招募信息及平台记录。", eyebrow="内容治理")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

competition_id = _query_competition_id()
if not competition_id:
    st.error("缺少 competition_id URL 参数")
    if st.button("返回竞赛管理页面", icon=":material/arrow_back:"):
        st.switch_page("admin_competitions.py")
    st.stop()

with st.spinner("正在加载竞赛详情..."):
    competition_data = _load_competition_detail(admin_token, competition_id)
if competition_data is not None:
    displayed_fields = set()

    for field, label in KNOWN_FIELDS:
        st.write(f"{label}：", competition_data.get(field, "未提供"))
        displayed_fields.add(field)

    extra_fields = {
        key: value
        for key, value in competition_data.items()
        if key not in displayed_fields
    }
    for field, value in extra_fields.items():
        st.write(f"{field}：", value)

st.divider()
if st.button("返回竞赛管理页面", icon=":material/arrow_back:"):
    st.switch_page("admin_competitions.py")
