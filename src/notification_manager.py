import logging
import os
from functools import lru_cache

from ai.circuit_breaker import ExternalAPIClient
from ai.config import get_settings

logger = logging.getLogger(__name__)


# Create cached client for external APIs
@lru_cache(maxsize=1)
def _get_notification_client(name: str) -> ExternalAPIClient:
    settings = get_settings()
    return ExternalAPIClient(
        name=f"notification_{name}",
        circuit_failure_threshold=settings.CIRCUIT_FAILURE_THRESHOLD,
        circuit_recovery_timeout=settings.CIRCUIT_RECOVERY_TIMEOUT,
        retry_attempts=settings.API_RETRY_ATTEMPTS,
        retry_backoff=settings.API_RETRY_BACKOFF,
    )


def send_slack_notification(webhook_url: str = None, text: str = "") -> dict:
    webhook = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        logger.warning("Slack webhook URL not configured - notification skipped")
        return {"success": False, "error": "No webhook URL provided", "skipped": True}

    client = _get_notification_client("slack")

    def _send():
        import requests

        logger.info("Sending Slack notification", extra={"webhook": webhook[:50]})
        response = requests.post(
            webhook, json={"text": text}, headers={"Content-Type": "application/json"}, timeout=30
        )
        return {"success": response.ok, "status_code": response.status_code}

    def _fallback():
        logger.error("Slack notification failed - circuit open")
        return {"success": False, "error": "Notification service unavailable", "circuit_open": True}

    try:
        return client.execute_with_protection(_send, fallback=_fallback)
    except Exception as e:
        logger.error(f"Slack notification error: {e}")
        return {"success": False, "error": str(e)}


def send_teams_notification(webhook_url: str = None, title: str = "", text: str = "") -> dict:
    webhook = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook:
        logger.warning("Teams webhook URL not configured - notification skipped")
        return {"success": False, "error": "No webhook URL provided", "skipped": True}

    client = _get_notification_client("teams")

    def _send():
        import requests

        logger.info("Sending Teams notification", extra={"webhook": webhook[:50]})
        message_card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": title,
            "themeColor": "0076D7",
            "title": title,
            "text": text,
        }
        response = requests.post(
            webhook, json=message_card, headers={"Content-Type": "application/json"}, timeout=30
        )
        return {"success": response.ok, "status_code": response.status_code}

    def _fallback():
        logger.error("Teams notification failed - circuit open")
        return {"success": False, "error": "Notification service unavailable", "circuit_open": True}

    try:
        return client.execute_with_protection(_send, fallback=_fallback)
    except Exception as e:
        logger.error(f"Teams notification error: {e}")
        return {"success": False, "error": str(e)}


def send_email_notification(
    smtp_config: dict = None, to_emails: list = None, subject: str = "", body: str = ""
) -> dict:
    if not smtp_config or not to_emails:
        return {"success": False, "error": "Missing SMTP config or recipients"}

    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()
        msg["From"] = smtp_config.get("sender")
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_config.get("host"), smtp_config.get("port", 587))
        server.starttls()
        server.login(smtp_config.get("user"), smtp_config.get("password"))
        server.send_message(msg)
        server.quit()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
