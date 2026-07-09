"""
Smart caching strategy for Convocatoria AI Engine.
Template caching, Redis backend with TTL.
"""

import json
import logging
from collections.abc import Callable
from functools import wraps
from hashlib import md5
from typing import Any

logger = logging.getLogger(__name__)

# Redis cache client (optional)
_redis_client = None


def get_redis_client():
    """Get Redis client if available."""
    global _redis_client
    if _redis_client is None:
        try:
            from ai.config import get_settings

            settings = get_settings()
            if settings.REDIS_URL:
                import redis

                _redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis cache client initialized")
        except Exception as e:
            logger.warning(f"Redis cache unavailable, using memory fallback: {e}")
    return _redis_client


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_parts = [str(a) for a in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return md5(":".join(key_parts).encode()).hexdigest()


def cached(ttl: int = 3600, prefix: str = "cache"):
    """
    Cache decorator with Redis backend.

    Args:
        ttl: Time to live in seconds
        prefix: Key prefix for namespacing
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis_client()
            key = f"{prefix}:{cache_key(*args, **kwargs)}"

            if redis:
                try:
                    cached = redis.get(key)
                    if cached:
                        logger.debug(f"Cache HIT: {key[:16]}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")

            # Execute function
            result = func(*args, **kwargs)

            if redis and result is not None:
                try:
                    redis.setex(key, ttl, json.dumps(result, default=str))
                    logger.debug(f"Cache SET: {key[:16]}")
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")

            return result

        return wrapper

    return decorator


class TemplateCache:
    """
    Cache for generated templates and convocatorias.
    """

    def __init__(self, ttl: int = 86400):  # 24 hours default
        self.ttl = ttl
        self._memory_cache: dict = {}
        self._redis = get_redis_client()

    def get(self, key: str) -> Any | None:
        """Get cached value."""
        if self._redis:
            try:
                cached = self._redis.get(f"template:{key}")
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any):
        """Set cached value."""
        key = f"template:{key}"
        if self._redis:
            try:
                self._redis.setex(key, self.ttl, json.dumps(value, default=str))
                return
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")

        self._memory_cache[key] = value


# Singleton cache
_template_cache: TemplateCache | None = None


def get_template_cache() -> TemplateCache:
    global _template_cache
    if _template_cache is None:
        _template_cache = TemplateCache()
    return _template_cache


@cached(ttl=300, prefix="convocatoria")
def get_cached_convocatoria(title: str, **kwargs) -> dict:
    """
    Example cached endpoint.
    Cache convocatoria templates for 5 minutes.
    """
    from ai.generator import generate_convocatoria

    return generate_convocatoria({"title": title}, **kwargs)
