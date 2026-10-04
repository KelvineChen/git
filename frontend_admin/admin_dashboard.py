from html import escape

import streamlit as st

from api_client import api_request
from ui import render_empty_state, render_metric_tile, render_page_intro


st.set_page_config(
    page_title="管理员控制台 - 知遇LinkLab",
    page_icon="🛠️",
    layout="wide",
)

render_page_intro("管理员控制台", "查看运营指标，管理用户、项目与反馈。", eyebrow="平台运营")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

admin_name = st.session_state.get("admin_name", "未知管理员")
admin_status = st.session_state.get("admin_status", "unknown")

st.markdown(
    f'<div class="zl-admin-banner"><strong>欢迎，{escape(str(admin_name))}</strong><br>'
    f'<span style="color:#64748B">当前状态：{escape(str(admin_status))}</span></div>',
    unsafe_allow_html=True,
)

with st.spinner("正在读取平台运营数据..."):
    statistics = api_request(
        "GET",
        "/api/admin/statistics",
        token=admin_token,
        success_message="运营数据已更新",
    )

if statistics is not None:
    metric_columns = st.columns(5)
    metric_data = (
        ("注册用户", statistics.get("users", 0), "violet", "group"),
        ("项目总数", statistics.get("projects", 0), "blue", "science"),
        ("正常项目", statistics.get("active_projects", 0), "green", "verified"),
        ("双方匹配", statistics.get("mutual_matches", 0), "cyan", "handshake"),
        ("待处理反馈", statistics.get("pending_feedback", 0), "amber", "feedback"),
    )
    for column, (label, value, accent, icon) in zip(metric_columns, metric_data):
        with column:
            render_metric_tile(label, value, accent=accent, icon=icon)

    chart_columns = st.columns(2)
    chart_data = (
        (chart_columns[0], "项目状态", statistics.get("project_statuses", {})),
        (chart_columns[1], "反馈状态", statistics.get("feedback_statuses", {})),
    )
    for column, title, counts in chart_data:
        with column:
            st.subheader(title)
            values = [{"状态": key, "数量": value} for key, value in counts.items()]
            if values:
                st.vega_lite_chart(
                    {
                        "data": {"values": values},
                        "mark": {"type": "arc", "innerRadius": 48, "outerRadius": 78},
                        "encoding": {
                            "theta": {"field": "数量", "type": "quantitative"},
                            "color": {
                                "field": "状态",
                                "type": "nominal",
                                "scale": {"range": ["#6D28D9", "#2563EB", "#0891B2", "#059669", "#D97706"]},
                            },
                            "tooltip": ["状态", "数量"],
                        },
                        "height": 180,
                    },
                    use_container_width=True,
                )
                status_labels = {
                    "recruiting": "招募中", "full": "已满员", "closed": "已关闭",
                    "completed": "已完成", "removed": "已下架", "pending": "待处理",
                    "reviewing": "处理中", "resolved": "已处理", "rejected": "已驳回",
                }
                for item in values:
                    label = status_labels.get(item["状态"], item["状态"])
                    st.write(f"{label}：{item['数量']}")
            else:
                render_empty_state("暂无数据", "当前还没有可用于统计的记录。", icon="donut_large")

st.subheader("管理功能")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("用户管理", icon=":material/group:", use_container_width=True):
        st.switch_page("admin_users.py")
with col2:
    if st.button("项目招募管理", icon=":material/science:", use_container_width=True):
        st.switch_page("admin_competitions.py")
with col3:
    if st.button("管理员审核", icon=":material/rate_review:", use_container_width=True):
        st.switch_page("admin_review.py")
with col4:
    if st.button("反馈处理", icon=":material/feedback:", use_container_width=True):
        st.switch_page("admin_feedback.py")
