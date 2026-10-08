"""Email verification API and privacy regression tests."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TEST_DB = ROOT / "tests" / ".email-verification-test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["EMAIL_VERIFICATION_ENABLED"] = "true"
os.environ["EMAIL_PROVIDER"] = "resend"
os.environ["EMAIL_API_KEY"] = "test-key"
os.environ["EMAIL_FROM"] = "LinkLab <test@example.com>"
os.environ["EMAIL_CODE_PEPPER"] = "test-pepper-that-is-not-used-in-production"

sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

import main  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from models import EmailVerification, User, UserSession  # noqa: E402


class EmailVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()
        TEST_DB.unlink(missing_ok=True)

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": "email-user",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123",
                "email": "User@Example.com",
                "school": "测试大学",
                "major": "计算机",
                "grade": "大三",
            },
        )
        self.assertEqual(response.status_code, 200)
        login = self.client.post(
            "/api/auth/login",
            json={"username": "email-user", "password": "StrongPass123"},
        )
        self.assertEqual(login.status_code, 200)
        self.token = login.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_session_token_is_hashed_and_logout_revokes_it(self):
        with SessionLocal() as db:
            session = db.scalar(select(UserSession))
            self.assertIsNotNone(session)
            self.assertNotEqual(session.token_hash, self.token)
            self.assertEqual(len(session.token_hash), 64)

        status = self.client.get("/api/email/status", headers=self.headers)
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["email"], "us***@example.com")

        self.assertEqual(
            self.client.post("/api/auth/logout", headers=self.headers).status_code,
            200,
        )
        rejected = self.client.get("/api/email/status", headers=self.headers)
        self.assertEqual(rejected.status_code, 401)

    def test_send_verify_and_contact_privacy(self):
        captured = {}

        def capture_email(to_email, code, expires_minutes):
            captured.update(email=to_email, code=code, expires=expires_minutes)

        with patch.object(main, "send_verification_email", side_effect=capture_email):
            sent = self.client.post("/api/email/send_code", headers=self.headers)
        self.assertEqual(sent.status_code, 200)
        self.assertRegex(captured["code"], r"^\d{6}$")
        self.assertEqual(captured["email"], "user@example.com")

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == "email-user"))
            verification = db.scalar(select(EmailVerification))
            self.assertNotEqual(verification.code_hash, captured["code"])
            self.assertEqual(main._contact_payload(user, None)["email"], "")

        repeated = self.client.post("/api/email/send_code", headers=self.headers)
        self.assertEqual(repeated.status_code, 429)
        self.assertEqual(repeated.json()["error"], "send_too_frequent")

        wrong = self.client.post(
            "/api/email/verify",
            headers=self.headers,
            json={"code": "000000" if captured["code"] != "000000" else "111111"},
        )
        self.assertEqual(wrong.status_code, 400)
        self.assertEqual(wrong.json()["remaining_attempts"], 4)

        verified = self.client.post(
            "/api/email/verify",
            headers=self.headers,
            json={"code": captured["code"]},
        )
        self.assertEqual(verified.status_code, 200)
        self.assertTrue(verified.json()["verified"])

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == "email-user"))
            payload = main._contact_payload(user, None)
            self.assertTrue(payload["email_verified"])
            self.assertEqual(payload["email"], "user@example.com")

    def test_email_routes_require_authentication(self):
        self.assertEqual(self.client.get("/api/email/status").status_code, 401)
        self.assertEqual(self.client.post("/api/email/send_code").status_code, 401)
        self.assertEqual(
            self.client.post("/api/email/verify", json={"code": "123456"}).status_code,
            401,
        )


if __name__ == "__main__":
    unittest.main()
