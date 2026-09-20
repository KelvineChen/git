import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"


def _error_code(response: requests.Response) -> str:
    try:
        return response.json().get("error", "request_failed")
    except ValueError:
        return "request_failed"


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

    try:
        response = requests.get(
            f"{BACKEND_URL}{path}",
            headers={"Authorization": f"Bearer {token}"},
            params=params if search else None,
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(_error_code(error.response))
        else:
            st.error("竞赛列表请求失败")
        return None
    except requests.RequestException:
        st.error("竞赛管理服务暂不可用，请稍后重试")
        return None
    except ValueError:
        st.error("竞赛管理服务返回的数据格式不正确")
        return None

    if isinstance(result, dict) and result.get("error"):
        st.error(str(result["error"]))
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

if search_submitted:
    competitions = _load_competitions(
        admin_token,
        search=True,
        params={
            "title": title.strip(),
            "creator": creator.strip(),
        },
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
