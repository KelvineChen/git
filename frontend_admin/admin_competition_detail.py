import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"
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


def _error_code(response: requests.Response) -> str:
    try:
        return response.json().get("error", "request_failed")
    except ValueError:
        return "request_failed"


def _load_competition_detail(
    token: str,
    competition_id: str,
) -> dict | None:
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/admin/competition/{competition_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as error:
        if error.response is not None:
            st.error(_error_code(error.response))
        else:
            st.error("竞赛详情请求失败")
        return None
    except requests.RequestException:
        st.error("竞赛详情服务暂不可用，请稍后重试")
        return None
    except ValueError:
        st.error("竞赛详情服务返回的数据格式不正确")
        return None

    if isinstance(result, dict) and result.get("error"):
        st.error(str(result["error"]))
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

st.title("竞赛详情")

admin_token = st.session_state.get("admin_token")
if not admin_token:
    st.warning("请先登录管理员账号")
    st.stop()

competition_id = _query_competition_id()
if not competition_id:
    st.error("缺少 competition_id URL 参数")
    if st.button("返回竞赛管理页面"):
        st.switch_page("admin_competitions.py")
    st.stop()

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
if st.button("返回竞赛管理页面"):
    st.switch_page("admin_competitions.py")
