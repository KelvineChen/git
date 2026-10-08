"""Email delivery adapter for account verification messages."""

from html import escape
import os

import requests


class EmailConfigurationError(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    pass


def email_verification_enabled() -> bool:
    return os.getenv("EMAIL_VERIFICATION_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def send_verification_email(
    to_email: str,
    code: str,
    expires_minutes: int,
) -> None:
    """Send one verification email without exposing provider details upstream."""
    if not email_verification_enabled():
        raise EmailConfigurationError("email verification is disabled")

    provider = os.getenv("EMAIL_PROVIDER", "resend").strip().lower()
    api_key = os.getenv("EMAIL_API_KEY", "").strip()
    sender = os.getenv("EMAIL_FROM", "").strip()
    if provider != "resend" or not api_key or not sender:
        raise EmailConfigurationError("email provider configuration is incomplete")

    safe_code = escape(code)
    subject = "知遇 LinkLab 邮箱验证码"
    text = (
        f"你的知遇 LinkLab 邮箱验证码是：{code}\n"
        f"验证码将在 {expires_minutes} 分钟后失效。\n"
        "如非本人操作，请忽略本邮件。"
    )
    html = f"""
    <div style="font-family:Arial,'Microsoft YaHei',sans-serif;color:#14213d;line-height:1.7">
      <h2 style="margin:0 0 16px">知遇 LinkLab 邮箱验证</h2>
      <p>你的验证码是：</p>
      <div style="font-size:30px;font-weight:700;letter-spacing:8px;margin:16px 0">
        {safe_code}
      </div>
      <p>验证码将在 {expires_minutes} 分钟后失效。</p>
      <p style="color:#64748b">如非本人操作，请忽略本邮件。</p>
    </div>
    """

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": sender,
                "to": [to_email],
                "subject": subject,
                "text": text,
                "html": html,
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise EmailDeliveryError("verification email delivery failed") from error
