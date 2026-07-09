"""
Intelligent alerting system for Convocatoria AI Engine.
Dead-letter queue, retry tracking, and notification alerts.
"""

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class FailedRequest:
    """Record of a failed API request."""

    timestamp: float
    endpoint: str
    error: str
    attempts: int
    payload: dict[str, Any] | None = None


class DeadLetterQueue:
    """
    Dead-letter queue for failed notifications.
    Stores failed requests for later retry or analysis.
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue: list[FailedRequest] = []

    def push(self, request: FailedRequest):
        """Add failed request to queue."""
        self._queue.append(request)
        if len(self._queue) > self.max_size:
            self._queue.pop(0)  # Remove oldest

        logger.warning(
            f"DLQ: Added failed request for {request.endpoint}",
            extra={"error": request.error, "attempts": request.attempts},
        )

    def get_failed(self) -> list[FailedRequest]:
        """Get all failed requests."""
        return self._queue.copy()

    def clear_resolved(self, max_age_hours: int = 24):
        """Remove old resolved failures."""
        cutoff = time.time() - (max_age_hours * 3600)
        self._queue = [r for r in self._queue if r.timestamp > cutoff]

    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": len(self._queue),
            "oldest_entry": min((r.timestamp for r in self._queue), default=None),
            "endpoint_breakdown": self._get_breakdown(),
        }

    def _get_breakdown(self) -> dict[str, int]:
        breakdown = {}
        for request in self._queue:
            breakdown[request.endpoint] = breakdown.get(request.endpoint, 0) + 1
        return breakdown


class AlertManager:
    """
    Manages alert delivery with deduplication and rate limiting.
    """

    def __init__(self, slack_webhook: str | None = None):
        self.slack_webhook = slack_webhook
        self._dlq = DeadLetterQueue()
        self._alert_counts: dict[str, int] = {}
        self._last_alert_time: dict[str, float] = {}
        self._alert_throttle_seconds = 300  # 5 minutes

    def send_alert(
        self, level: AlertLevel, title: str, message: str, details: dict[str, Any] | None = None
    ):
        """Send alert with deduplication."""
        key = f"{level.value}:{title}"

        # Throttle alerts
        now = time.time()
        if key in self._last_alert_time:
            if now - self._last_alert_time[key] < self._alert_throttle_seconds:
                self._alert_counts[key] = self._alert_counts.get(key, 0) + 1
                return

        self._last_alert_time[key] = now
        self._alert_counts[key] = 1

        payload = {
            "level": level.value,
            "title": title,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
            "details": details or {},
        }

        if self.slack_webhook:
            self._send_slack_alert(payload)
        else:
            logger.log(level=level.value, msg=f"[ALERT] {title}: {message}")

    def _send_slack_alert(self, payload: dict[str, Any]):
        """Send alert to Slack."""
        try:
            import requests

            requests.post(
                self.slack_webhook,
                json={"text": f"🚨 {payload['title']}\n{payload['message']}"[:3000]},
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def record_failure(
        self, endpoint: str, error: str, attempts: int, payload: dict[str, Any] | None = None
    ):
        """Record failed request and potentially alert."""
        failed = FailedRequest(
            timestamp=time.time(),
            endpoint=endpoint,
            error=error,
            attempts=attempts,
            payload=payload,
        )
        self._dlq.push(failed)

        # Alert on critical failures
        if attempts >= 3:
            self.send_alert(
                AlertLevel.ERROR,
                f"API Failure: {endpoint}",
                f"Failed after {attempts} attempts: {error[:200]}",
                {"payload": str(payload)[:500]},
            )


# Global instances
_dlq = DeadLetterQueue()
_alert_manager: AlertManager | None = None


def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        from ai.config import get_settings

        settings = get_settings()
        _alert_manager = AlertManager(slack_webhook=settings.SLACK_WEBHOOK_URL)
    return _alert_manager


def get_dlq() -> DeadLetterQueue:
    return _dlq
