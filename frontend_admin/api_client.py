import os
from typing import Any

import requests
import streamlit as st
from ui import render_request_error


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
    show_success: bool | None = None,
) -> Any | None:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    identity = f"admin:{method}:{path}:{sorted((params or {}).items())}"
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
        render_request_error("网络异常，请稍后重试", method=method, identity=identity, retryable=True)
        return None
    except ValueError:
        render_request_error("后端返回的数据格式不正确", method=method, identity=identity, retryable=True)
        return None

    if not isinstance(result, (dict, list)):
        render_request_error("后端返回的数据格式不正确", method=method, identity=identity, retryable=True)
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
        render_request_error(message, method=method, identity=identity,
                             retryable=response.status_code >= 500, status_code=response.status_code)
        return None

    notify_success = show_success if show_success is not None else method.upper() != "GET"
    if notify_success:
        st.success(success_message)
        st.toast(success_message, icon=":material/check_circle:")
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    return result
