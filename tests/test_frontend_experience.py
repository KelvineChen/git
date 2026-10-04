"""Offline UI regression tests; run with unittest and frontend dependencies."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "frontend_admin"))
APP = ROOT / "frontend" / "app.py"
PROFILE = {
    "success": True, "skills": ["Python", "SQL"],
    "skill_levels": {"Python": "熟练", "SQL": "进阶"},
    "experience": ["科研数据分析"], "interests": ["机器学习"],
    "preference": "异步协作", "time_commitment": "每周10小时",
    "raw_text": "掌握Python和SQL", "contact_method": "wechat",
    "contact_value": "test-contact", "contact_visible": True,
}


def response(data, status=200):
    value = Mock(status_code=status, ok=status < 400)
    value.json.return_value = data
    if status >= 400:
        value.raise_for_status.side_effect = requests.HTTPError(response=value)
    return value


def user_get(url, **kwargs):
    if "/api/profile/" in url:
        return response(PROFILE)
    return response({"success": True, "matches": [], "projects": [], "unread_count": 0})


def user_app(page="我的画像"):
    app = AppTest.from_file(str(APP), default_timeout=20)
    for key, value in {
        "user_id": 42, "username": "测试用户", "school": "测试大学",
        "token": "test-token", "app_page": page,
    }.items():
        app.session_state[key] = value
    return app.run()


def level(app, name):
    return next(item for item in app.selectbox if item.label == name)


class FrontendExperienceTests(unittest.TestCase):
    def assert_clean(self, app):
        self.assertFalse(app.exception, str(app.exception))

    @patch("requests.get", side_effect=user_get)
    def test_skill_edit_add_remove_and_save(self, get):
        app = user_app()
        self.assert_clean(app)
        self.assertFalse(app.success)
        self.assertEqual(level(app, "SQL").value, "进阶")
        self.assertFalse(any(item.label == "技能等级（JSON对象）" for item in app.text_area))
        level(app, "Python").select("了解").run()
        app.text_area(key="profile_skills").set_value("Python\nNLP\nPython").run()
        self.assertEqual(level(app, "Python").value, "了解")
        self.assertEqual(level(app, "NLP").value, "")
        self.assertFalse(any(item.label == "SQL" for item in app.selectbox))
        level(app, "NLP").select("掌握").run()
        with patch("requests.post", return_value=response({"success": True})) as post:
            next(item for item in app.button if item.label == "保存画像").click().run()
        self.assert_clean(app)
        data = post.call_args.kwargs["json"]["parsed_data"]
        self.assertEqual(data["skills"], ["Python", "NLP"])
        self.assertEqual(data["skill_levels"], {"Python": "了解", "NLP": "掌握"})
        self.assertTrue(any(item.value == "画像保存成功" for item in app.success))

    @patch("requests.get", side_effect=user_get)
    def test_reparse_updates_existing_levels(self, get):
        app = user_app()
        data = dict(PROFILE, skill_levels={"Python": "掌握", "SQL": "了解"})
        with patch("requests.post", return_value=response({"success": True, "data": data})):
            app.button(key="parse_profile_button").click().run()
        self.assert_clean(app)
        self.assertEqual(level(app, "Python").value, "掌握")
        self.assertEqual(level(app, "SQL").value, "了解")

    def test_failed_profile_read_retries_without_defaulting_contacts(self):
        def offline(url, **kwargs):
            if "/api/profile/" in url:
                raise requests.ConnectionError("offline")
            return user_get(url, **kwargs)
        with patch("requests.get", side_effect=offline):
            app = user_app()
        self.assert_clean(app)
        self.assertNotIn("contact_loaded_42", app.session_state)
        retry = next(item for item in app.button if item.label == "重新加载")
        with patch("requests.get", side_effect=user_get) as get:
            retry.click().run()
        self.assert_clean(app)
        profile_calls = [call for call in get.call_args_list if "/api/profile/" in call.args[0]]
        self.assertEqual(len(profile_calls), 1)
        self.assertEqual(app.session_state["contact_value"], "test-contact")
        self.assertFalse(app.error)

    @patch("requests.get", side_effect=user_get)
    def test_writes_are_not_automatically_replayed(self, get):
        app = user_app()
        with patch("requests.post", side_effect=requests.Timeout("offline")) as post:
            next(item for item in app.button if item.label == "保存画像").click().run()
            self.assert_clean(app)
            self.assertTrue(any("保存画像" in item.value and "已保留" in item.value for item in app.caption))
            app.run()
            self.assertEqual(post.call_count, 1)
        self.assertEqual(level(app, "Python").value, "熟练")

    def test_malformed_and_server_error_show_retry(self):
        for value in (response([], 200), response({}, 503)):
            def get(url, **kwargs):
                return value if "/api/match_list/" in url else user_get(url, **kwargs)
            with self.subTest(status=value.status_code), patch("requests.get", side_effect=get):
                app = user_app("匹配推荐")
            self.assert_clean(app)
            self.assertTrue(app.error)
            self.assertTrue(any(item.label == "重新加载" for item in app.button))

    @patch("requests.get", side_effect=user_get)
    def test_missing_profile_is_not_a_network_error(self, get):
        def empty(url, **kwargs):
            if "/api/profile/" in url:
                return response({"success": False, "message": "画像不存在"})
            return user_get(url, **kwargs)
        get.side_effect = empty
        app = user_app()
        self.assert_clean(app)
        self.assertFalse(app.error)
        self.assertTrue(app.button(key="parse_profile_button"))

    def test_admin_reads_are_quiet_and_writes_have_feedback(self):
        script = """
from api_client import api_request
import streamlit as st
with st.spinner('正在读取数据...'):
    api_request('GET', '/api/admin/users', success_message='读取成功')
if st.button('保存'):
    with st.spinner('正在保存...'):
        api_request('POST', '/api/admin/test', success_message='保存成功')
"""
        with patch("requests.request", return_value=response({"success": True, "data": []})) as request:
            app = AppTest.from_string(script, default_timeout=20).run()
            self.assert_clean(app)
            self.assertFalse(app.success)
            app.button[0].click().run()
            self.assert_clean(app)
            self.assertTrue(any(item.value == "保存成功" for item in app.success))
        self.assertTrue(any(call.args[0] == "POST" for call in request.call_args_list))

    def test_admin_search_retry_retains_filters(self):
        with patch("requests.request", return_value=response({"success": True, "data": []})), patch("streamlit.page_link"):
            app = AppTest.from_file(str(ROOT / "frontend_admin" / "admin_users.py"), default_timeout=20)
            app.session_state["admin_token"] = "test-token"
            app.run()
            next(item for item in app.text_input if item.label == "学校").set_value("测试大学").run()
            with patch("requests.request", side_effect=requests.ConnectionError("offline")):
                next(item for item in app.button if item.label == "搜索").click().run()
            self.assert_clean(app)
            retry = next(item for item in app.button if item.label == "重新加载")
            with patch("requests.request", return_value=response({"success": True, "data": []})) as request:
                retry.click().run()
            self.assert_clean(app)
            self.assertEqual(request.call_args.kwargs["params"]["school"], "测试大学")
            self.assertTrue(request.call_args.args[1].endswith('/api/admin/users/search'))


if __name__ == "__main__":
    unittest.main()
