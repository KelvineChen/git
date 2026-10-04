import os
from typing import Any

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def api_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json: dict | None = None,
    params: dict | None = None,
    success_message: str,
    error_messages: dict[str, str] | None = None,
    timeout: int = 15,
) -> Any | None:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    try:
        response = requests.request(
            method,
            f"{BACKEND_URL}{path}",
            headers=headers,
            json=json,
            params=params,
            timeout=timeout,
        )
        result = response.json()
    except requests.RequestException:
        st.error("网络异常，请稍后重试")
        return None
    except ValueError:
        st.error("后端返回的数据格式不正确")
        return None

    error_code = result.get("error") if isinstance(result, dict) else None
    success = response.ok and not error_code
    if isinstance(result, dict) and "success" in result:
        success = success and bool(result["success"])
    elif isinstance(result, dict) and "status" in result:
        success = success and result["status"] == "ok"

    if not success:
        message = "操作失败，请稍后重试"
        if isinstance(result, dict):
            message = str(result.get("message") or error_code or message)
        if error_messages and error_code in error_messages:
            message = error_messages[error_code]
        st.error(message)
        return None

    st.success(success_message)
    st.toast(success_message, icon=":material/check_circle:")
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    return result
