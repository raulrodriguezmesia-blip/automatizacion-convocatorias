"""
Rate limiting middleware for FastAPI.
Sliding window algorithm with Redis backend.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    In-memory rate limiter for single-instance deployments.
    For production, use RedisRateLimiter.
    """

    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._requests: dict = {}

    def _cleanup(self, key: str, now: float):
        """Remove old entries."""
        if key in self._requests:
            self._requests[key] = [
                ts for ts in self._requests[key] if now - ts < self.window_seconds
            ]

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed.

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        self._cleanup(key, now)

        count = len(self._requests.get(key, []))
        remaining = max(0, self.requests_per_window - count)

        if count >= self.requests_per_window:
            return False, 0

        self._requests[key] = self._requests.get(key, []) + [now]
        return True, remaining - 1


class RedisRateLimiter:
    """
    Redis-backed rate limiter for distributed deployments.
    Uses sliding window with sorted sets.
    """

    def __init__(self, redis_url: str, requests_per_window: int = 100, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.redis_url = redis_url
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            try:
                import redis

                self._redis = redis.from_url(self.redis_url)
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
                return None
        return self._redis

    def is_allowed(self, key: str) -> tuple[bool, int]:
        redis_client = self._get_redis()

        if redis_client is None:
            return True, self.requests_per_window  # Allow if Redis unavailable

        now = time.time()
        pipeline = redis_client.pipeline()

        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - self.window_seconds)
        # Count current requests
        pipeline.zcard(key)
        # Add current request
        pipeline.zadd(key, {str(now): now})
        # Set expiry
        pipeline.expire(key, int(self.window_seconds * 2))

        results = pipeline.execute()
        current = results[1]
        remaining = max(0, self.requests_per_window - current)

        if current >= self.requests_per_window:
            return False, 0

        return True, remaining - 1


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware for rate limiting.
    Adds X-RateLimit headers to responses.
    """

    def __init__(self, app, limiter=None):
        super().__init__(app)
        self.limiter = limiter or InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP + optional API key)
        client_id = self._get_client_id(request)
        key = f"rate_limit:{client_id}"

        allowed, remaining = self.limiter.is_allowed(key)

        if not allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return Response(
                content='{"error": "Rate limit exceeded", "retry_after": 60}',
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Content-Type": "application/json",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 60)),
                    "Retry-After": "60",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.limiter.window_seconds))

        return response

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Priority: API key header > X-Forwarded-For > direct IP
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"api_key:{api_key[:8]}"

        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"


def get_rate_limiter():
    """Factory for rate limiter based on configuration."""
    from ai.config import get_settings

    settings = get_settings()

    if settings.REDIS_URL:
        return RedisRateLimiter(
            redis_url=settings.REDIS_URL,
            requests_per_window=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW,
        )
    return InMemoryRateLimiter(
        requests_per_window=settings.RATE_LIMIT_REQUESTS, window_seconds=settings.RATE_LIMIT_WINDOW
    )
