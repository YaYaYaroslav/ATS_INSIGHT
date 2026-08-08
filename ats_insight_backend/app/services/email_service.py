import logging
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_raw_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        logger.info("=" * 60)
        logger.info("EMAIL (SMTP не налаштовано — показую замість реальної відправки)")
        logger.info("To: %s", to_email)
        logger.info("Subject: %s", subject)
        logger.info("\n%s", body)
        logger.info("=" * 60)
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception:
        logger.exception("Не вдалося надіслати email на %s", to_email)


def generate_verification_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    return token, expires


def send_verification_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    subject = "Підтвердь свій email — ATS Insight"
    body = (
        "Привіт!\n\n"
        "Щоб підтвердити email та активувати акаунт в ATS Insight, перейди за посиланням:\n"
        f"{link}\n\n"
        f"Посилання дійсне {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} год.\n\n"
        "Якщо ти не реєструвався(лась) в ATS Insight — просто проігноруй цей лист."
    )
    _send_raw_email(to_email, subject, body)
