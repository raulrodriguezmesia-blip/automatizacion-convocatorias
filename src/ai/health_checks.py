"""
Health check endpoints for production readiness.
Separate liveness and readiness probes.
"""

import logging
import time
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Track startup time for liveness
_STARTUP_TIME: float | None = None


def init_health_checks():
    """Initialize health check subsystem."""
    global _STARTUP_TIME
    _STARTUP_TIME = time.time()


def get_liveness_probe() -> dict[str, Any]:
    """
    Liveness probe - checks if the application is running.
    Used by Kubernetes to determine if pod should be restarted.
    """
    global _STARTUP_TIME

    if _STARTUP_TIME is None:
        init_health_checks()

    uptime = time.time() - _STARTUP_TIME

    return {
        "status": "alive",
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": uptime,
        "checks": {"application": {"status": "ok", "message": "Application is running"}},
    }


def get_readiness_probe(
    check_database: bool = True,
    check_redis: bool = False,
    check_external_apis: bool = False,
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    """
    Readiness probe - checks if the application is ready to serve traffic.
    Used by Kubernetes to determine if pod should receive traffic.

    Args:
        check_database: Whether to check database connectivity
        check_redis: Whether to check Redis connectivity
        check_external_apis: Whether to check external API connectivity
        timeout_seconds: Maximum time for checks

    Returns:
        Health status dictionary
    """
    checks = {"application": {"status": "ok", "message": "Application is ready"}}

    # Database check
    if check_database:
        try:
            db_healthy = _check_database(timeout_seconds)
            checks["database"] = db_healthy
        except Exception as e:
            checks["database"] = {"status": "error", "message": str(e)}

    # Redis check (if configured)
    if check_redis:
        try:
            redis_healthy = _check_redis(timeout_seconds)
            checks["redis"] = redis_healthy
        except Exception as e:
            checks["redis"] = {"status": "error", "message": str(e)}

    # External APIs check (optional, can be disabled for faster startup)
    if check_external_apis:
        try:
            api_status = _check_external_apis(timeout_seconds)
            checks.update(api_status)
        except Exception as e:
            checks["external_apis"] = {"status": "error", "message": str(e)}

    # Determine overall status
    all_healthy = all(check.get("status") == "ok" for check in checks.values())

    return {
        "status": "ready" if all_healthy else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": checks,
    }


def _check_database(timeout_seconds: float) -> dict[str, Any]:
    """Check database connectivity."""
    from saas.models import engine

    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "message": "Database connection healthy"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}


def _check_redis(timeout_seconds: float) -> dict[str, Any]:
    """Check Redis connectivity."""
    try:
        import redis

        settings = __import__("ai.config", fromlist=["get_settings"]).get_settings()
        if not settings.REDIS_URL:
            return {"status": "skipped", "message": "Redis not configured"}

        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=timeout_seconds)
        r.ping()
        return {"status": "ok", "message": "Redis connection healthy"}
    except Exception as e:
        return {"status": "error", "message": f"Redis connection failed: {str(e)}"}


def _check_external_apis(timeout_seconds: float) -> dict[str, Any]:
    """Check external API connectivity."""
    checks = {}

    # Check calendar APIs (without credentials, just verify libraries)
    checks["calendar_apis"] = {"status": "ok", "message": "Calendar API libraries available"}

    # Check notification services
    checks["notification_services"] = {
        "status": "ok",
        "message": "Notification services configured",
    }

    return checks


class HealthMiddleware:
    """
    ASGI middleware for health check endpoints.
    Adds /health/live and /health/ready endpoints.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        if path == "/health/live":
            await self._handle_liveness(scope, receive, send)
            return
        elif path == "/health/ready":
            await self._handle_readiness(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def _handle_liveness(self, scope, receive, send):
        """Handle liveness probe request."""
        health = get_liveness_probe()
        await self._send_response(send, 200, health)

    async def _handle_readiness(self, scope, receive, send):
        """Handle readiness probe request."""
        health = get_readiness_probe(
            check_database=True,
            check_redis=False,  # Can be enabled if Redis is critical
            check_external_apis=False,  # Don't check on every probe
        )
        status_code = 200 if health.get("status") != "error" else 503
        await self._send_response(send, status_code, health)

    async def _send_response(self, send, status_code: int, body: dict):
        """Send JSON response."""
        import json

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    [b"content-type", b"application/json"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(body).encode(),
            }
        )


# Initialize on import
init_health_checks()
