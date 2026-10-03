import streamlit as st

from api_client import api_request


st.set_page_config(
    page_title="反馈处理 - 知遇LinkLab",
    page_icon=":material/feedback:",
    layout="wide",
)


def chart_from_counts(counts: dict, title: str) -> None:
    values = [{"名称": str(key), "数量": int(value)} for key, value in counts.items()]
    if not values:
        st.caption("暂无数据")
        return
    st.vega_lite_chart(
        {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": values},
            "mark": {"type": "arc", "innerRadius": 45},
            "encoding": {
                "theta": {"field": "数量", "type": "quantitative"},
                "color": {"field": "名称", "type": "nominal", "title": title},
                "tooltip": [
                    {"field": "名称", "type": "nominal"},
                    {"field": "数量", "type": "quantitative"},
                ],
            },
            "view": {"stroke": None},
            "height": 230,
        },
        use_container_width=True,
    )


st.title("反馈处理")
admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

status_filter = st.selectbox(
    "状态筛选",
    options=["all", "pending", "reviewing", "resolved", "rejected"],
    format_func=lambda value: {
        "all": "全部",
        "pending": "待处理",
        "reviewing": "处理中",
        "resolved": "已处理",
        "rejected": "已驳回",
    }[value],
)

with st.spinner("正在读取反馈数据..."):
    result = api_request(
        "GET",
        "/api/admin/feedback",
        token=admin_token,
        params={"status": status_filter},
        success_message="反馈数据已更新",
    )
if result is None:
    st.stop()

statistics = result.get("statistics", {})
metrics = st.columns(3)
metrics[0].metric("反馈总数", statistics.get("total", 0))
metrics[1].metric("待处理", statistics.get("by_status", {}).get("pending", 0))
metrics[2].metric("已处理", statistics.get("by_status", {}).get("resolved", 0))

chart_columns = st.columns(2)
with chart_columns[0]:
    st.subheader("反馈类型分布")
    chart_from_counts(statistics.get("by_category", {}), "反馈类型")
with chart_columns[1]:
    st.subheader("处理状态分布")
    chart_from_counts(statistics.get("by_status", {}), "处理状态")

status_labels = {
    "pending": "待处理",
    "reviewing": "处理中",
    "resolved": "已处理",
    "rejected": "已驳回",
}
feedbacks = result.get("feedback", [])
if not feedbacks:
    st.info("当前筛选下没有反馈")

for item in feedbacks:
    with st.expander(
        f"#{item['feedback_id']} · {item['category']} · "
        f"{item['username']} · {status_labels.get(item['status'], item['status'])}"
    ):
        st.write(item["content"])
        st.caption(
            f"来源页面：{item.get('source_page') or '未记录'} · "
            f"联系邮箱：{item.get('contact_email') or '未提供'} · "
            f"提交时间：{str(item.get('created_at') or '')[:16]}"
        )
        with st.form(f"feedback_reply_{item['feedback_id']}"):
            next_status = st.selectbox(
                "处理状态",
                list(status_labels),
                index=list(status_labels).index(item["status"])
                if item["status"] in status_labels
                else 0,
                format_func=lambda value: status_labels[value],
            )
            reply = st.text_area("回复内容", value=item.get("admin_reply") or "")
            submitted = st.form_submit_button("保存处理结果", type="primary")
        if submitted:
            with st.spinner("正在保存处理结果..."):
                saved = api_request(
                    "POST",
                    f"/api/admin/feedback/{item['feedback_id']}/reply",
                    token=admin_token,
                    json={
                        "admin_name": st.session_state.get("admin_name", ""),
                        "status": next_status,
                        "admin_reply": reply,
                    },
                    success_message="反馈处理结果已保存",
                )
            if saved is not None:
                st.rerun()
