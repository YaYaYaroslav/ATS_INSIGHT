"""Email Service.

If RESEND_API_KEY is not configured, emails are logged instead of sent, so the
verification flow can be tested locally without a real mail provider.

Uses the Resend HTTP API (https://resend.com) instead of raw SMTP, because
many hosting providers (e.g. Render's free tier) block outbound SMTP ports
(25/465/587) but allow normal HTTPS traffic.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _send_raw_email(to_email: str, subject: str, body: str) -> None:
    if not settings.RESEND_API_KEY:
        logger.info("=" * 60)
        logger.info("EMAIL (RESEND_API_KEY not configured — showing instead of sending)")
        logger.info("To: %s", to_email)
        logger.info("Subject: %s", subject)
        logger.info("\n%s", body)
        logger.info("=" * 60)
        return

    payload = {
        "from": settings.SMTP_FROM,  # e.g. "onboarding@resend.dev" or a verified sender
        "to": [to_email],
        "subject": subject,
        "text": body,
    }
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception:
        logger.exception("Failed to send email to %s", to_email)


def generate_verification_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    return token, expires


def send_verification_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    subject = "Verify your email — ATS Insight"
    body = (
        "Hi!\n\n"
        "To verify your email and activate your ATS Insight account, follow this link:\n"
        f"{link}\n\n"
        f"The link is valid for {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.\n\n"
        "If you didn't sign up for ATS Insight, just ignore this email."
    )
    _send_raw_email(to_email, subject, body)
