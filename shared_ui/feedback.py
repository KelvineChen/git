"""Request recovery controls shared by both Streamlit applications."""

from hashlib import sha256

import streamlit as st


def render_request_error(
    message: str,
    *,
    method: str,
    identity: str,
    retryable: bool = False,
    status_code: int | None = None,
    action_label: str = "原操作按钮",
) -> None:
    st.error(message)
    if status_code == 401:
        st.caption("登录状态已失效，请退出后重新登录。")
    elif status_code == 403:
        st.caption("当前账号无权执行此操作，请核对账号权限。")
    elif retryable and method.upper() == "GET":
        key = sha256(identity.encode("utf-8")).hexdigest()[:20]
        # A click reruns the page and its read request; never replay writes here.
        st.button("重新加载", key=f"request_retry_{key}", icon=":material/refresh:")
    elif retryable:
        st.caption(
            f"输入内容已保留。请先确认操作是否已生效，再点击“{action_label}”重新提交。"
        )
    else:
        st.caption("请核对输入内容或当前操作条件后重试。")
