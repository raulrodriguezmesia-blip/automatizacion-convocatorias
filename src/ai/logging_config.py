"""
Structured JSON Logging for Convocatoria AI Engine.
Production-ready with correlation IDs and proper log levels.
"""

import logging
import sys
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records."""

    def __init__(self):
        super().__init__()
        self._correlation_id: str | None = None

    def filter(self, record):
        record.correlation_id = self._correlation_id or "unknown"
        record.timestamp = datetime.now(UTC).isoformat()
        return True

    def set_correlation_id(self, correlation_id: str):
        self._correlation_id = correlation_id


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno


def setup_logging(
    level: str = "INFO", json_output: bool = True, log_format: str | None = None
) -> CorrelationIdFilter:
    """
    Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Whether to output logs in JSON format
        log_format: Custom format string (optional)

    Returns:
        CorrelationIdFilter instance for request correlation
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create stdout handler
    handler = logging.StreamHandler(sys.stdout)

    # Create correlation ID filter
    correlation_filter = CorrelationIdFilter()
    handler.addFilter(correlation_filter)

    if json_output:
        formatter = JSONFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s %(module)s %(function)s %(line)s correlation_id"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s [%(correlation_id)s]"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)

    return correlation_filter


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the standard configuration."""
    return logging.getLogger(name)
