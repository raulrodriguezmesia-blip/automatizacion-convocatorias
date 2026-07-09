"""
Circuit Breaker and Retry patterns for external API calls.
Protects against cascading failures and implements exponential backoff.
"""

import logging
import threading
import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents calls to failing services and allows recovery.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exceptions: tuple = (Exception,),
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.expected_exceptions):
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = time.time()
                logger.warning(
                    f"Circuit breaker '{self.name}' recorded failure "
                    f"(count: {self._failure_count}/{self.failure_threshold})"
                )

                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.error(
                        f"Circuit breaker '{self.name}' is now OPEN - "
                        f"blocking calls for {self.recovery_timeout}s"
                    )
            return False  # Don't suppress the exception
        else:
            with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info(f"Circuit breaker '{self.name}' is now CLOSED")
            return False

    def call(
        self,
        func: Callable[[], T] | None = None,
        *,
        operation: Callable[[], T] | None = None,
        fallback: Callable[[], T] | None = None,
    ) -> T:
        """Execute function with circuit breaker protection.

        Accepts the callable either positionally (``func``) or via the
        ``operation`` keyword for readability. If the circuit is OPEN and a
        ``fallback`` is provided, the fallback is returned instead of raising.
        """
        target = func if func is not None else operation
        if target is None:
            raise ValueError("CircuitBreaker.call requires 'func' or 'operation'")

        with self._lock:
            if self._state == CircuitState.OPEN:
                if (
                    self._last_failure_time
                    and time.time() - self._last_failure_time > self.recovery_timeout
                ):
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' is HALF_OPEN - testing recovery")
                else:
                    if fallback is not None:
                        return fallback()
                    raise CircuitBreakerOpen(
                        f"Circuit breaker '{self.name}' is OPEN - call blocked"
                    )

        try:
            result = target()
            with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info(f"Circuit breaker '{self.name}' recovered - now CLOSED")
            return result
        except self.expected_exceptions:
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = time.time()
                logger.warning(
                    f"Circuit breaker '{self.name}' failure {self._failure_count}/{self.failure_threshold}"
                )
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.error(f"Circuit breaker '{self.name}' is now OPEN")
            if fallback is not None:
                return fallback()
            raise

    def state(self) -> CircuitState:
        """Get current circuit state.

        Transitions OPEN -> HALF_OPEN lazily once ``recovery_timeout`` has
        elapsed, so callers can inspect readiness without invoking a call.
        """
        with self._lock:
            if (
                self._state == CircuitState.OPEN
                and self._last_failure_time is not None
                and time.time() - self._last_failure_time > self.recovery_timeout
            ):
                self._state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' is HALF_OPEN - testing recovery")
            return self._state


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    pass


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.0,
    max_backoff: float = 30.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Decorator for retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Base backoff time in seconds
        max_backoff: Maximum backoff time
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions that should be retried

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception: Exception | None = None

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    attempt += 1

                    if attempt < max_attempts:
                        backoff = min(backoff_factor * (2 ** (attempt - 1)), max_backoff)
                        if jitter:
                            import random

                            backoff *= 0.5 + random.random() * 0.5

                        logger.warning(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__} "
                            f"after {type(e).__name__}: {str(e)[:100]}"
                        )
                        time.sleep(backoff)

            raise last_exception or RuntimeError("Unknown error")

        return wrapper

    return decorator


class ExternalAPIClient:
    """
    Base client for external APIs with circuit breaker and retry built-in.
    """

    def __init__(
        self,
        name: str,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 60.0,
        retry_attempts: int = 3,
        retry_backoff: float = 1.0,
    ):
        self.name = name
        self.circuit_breaker = CircuitBreaker(
            name=name,
            failure_threshold=circuit_failure_threshold,
            recovery_timeout=circuit_recovery_timeout,
        )
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff

    def execute_with_protection(
        self, operation: Callable[[], T], fallback: Callable[[], T] | None = None
    ) -> T:
        """
        Execute operation with circuit breaker and retry.

        Args:
            operation: The operation to execute
            fallback: Optional fallback operation if circuit is open

        Returns:
            Result from operation or fallback
        """
        if self.circuit_breaker.state() == CircuitState.OPEN and fallback:
            logger.info(f"Using fallback for {self.name} - circuit is OPEN")
            return fallback()

        @with_retry(max_attempts=self.retry_attempts, backoff_factor=self.retry_backoff)
        def _execute():
            return self.circuit_breaker.call(operation)

        try:
            return _execute()
        except CircuitBreakerOpen:
            if fallback:
                logger.info(f"Falling back for {self.name}")
                return fallback()
            raise
