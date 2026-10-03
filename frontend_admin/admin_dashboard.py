import streamlit as st

from api_client import api_request


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

with st.spinner("正在读取平台运营数据..."):
    statistics = api_request(
        "GET",
        "/api/admin/statistics",
        token=admin_token,
        success_message="运营数据已更新",
    )

if statistics is not None:
    metric_columns = st.columns(5)
    metric_columns[0].metric("注册用户", statistics.get("users", 0))
    metric_columns[1].metric("项目总数", statistics.get("projects", 0))
    metric_columns[2].metric("正常项目", statistics.get("active_projects", 0))
    metric_columns[3].metric("双方匹配", statistics.get("mutual_matches", 0))
    metric_columns[4].metric("待处理反馈", statistics.get("pending_feedback", 0))

    chart_columns = st.columns(2)
    chart_data = (
        (chart_columns[0], "项目状态", statistics.get("project_statuses", {}), "#2764e7"),
        (chart_columns[1], "反馈状态", statistics.get("feedback_statuses", {}), "#0b8f83"),
    )
    for column, title, counts, color in chart_data:
        with column:
            st.subheader(title)
            values = [{"状态": key, "数量": value} for key, value in counts.items()]
            if values:
                st.vega_lite_chart(
                    {
                        "data": {"values": values},
                        "mark": {"type": "bar", "cornerRadiusEnd": 5, "color": color},
                        "encoding": {
                            "x": {"field": "数量", "type": "quantitative", "title": "数量"},
                            "y": {"field": "状态", "type": "nominal", "title": None},
                            "tooltip": ["状态", "数量"],
                        },
                        "height": 180,
                    },
                    use_container_width=True,
                )
            else:
                st.caption("暂无数据")

st.subheader("管理功能")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("用户管理", use_container_width=True):
        st.switch_page("admin_users.py")
with col2:
    if st.button("竞赛招募管理", use_container_width=True):
        st.switch_page("admin_competitions.py")
with col3:
    if st.button("管理员审核", use_container_width=True):
        st.switch_page("admin_review.py")
with col4:
    if st.button("反馈处理", use_container_width=True):
        st.switch_page("admin_feedback.py")
