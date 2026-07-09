"""
OpenTelemetry distributed tracing for Convocatoria AI Engine.
Provides end-to-end request correlation across services.
"""

import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind, get_tracer

logger = logging.getLogger(__name__)

# OpenTelemetry configuration
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() == "true"
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "convocatorias-ai")
OTEL_SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")

_tracer_provider: TracerProvider | None = None


def init_telemetry():
    """Initialize OpenTelemetry tracing."""
    global _tracer_provider

    if not OTEL_ENABLED:
        logger.info("OpenTelemetry disabled")
        return None

    _tracer_provider = TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: OTEL_SERVICE_NAME,
                SERVICE_VERSION: OTEL_SERVICE_VERSION,
            }
        )
    )

    # Configure OTLP exporter
    try:
        exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
        _tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(_tracer_provider)
        logger.info(f"OpenTelemetry initialized, exporting to {OTEL_ENDPOINT}")
        return _tracer_provider
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry: {e}")
        return None


def instrument_fastapi(app):
    """Instrument FastAPI application."""
    if _tracer_provider:
        FastAPIInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        logger.info("FastAPI instrumented")


def get_tracer_instance(name: str = __name__):
    """Get a tracer instance from the OpenTelemetry API."""
    return get_tracer(name)


def start_span(name: str, kind: SpanKind = SpanKind.INTERNAL, **attributes):
    """
    Start a span with optional attributes.

    Args:
        name: Span name
        kind: Span kind (INTERNAL, CLIENT, SERVER, etc.)
        **attributes: Key-value attributes to add to span

    Returns:
        Context manager for the span
    """
    if not _tracer_provider:
        return _NoopSpan()

    tracer = get_tracer_instance()
    span = tracer.start_span(name, kind=kind)

    for key, value in attributes.items():
        span.set_attribute(key, value)

    return _SpanContext(span)


class _SpanContext:
    """Context manager wrapper for spans."""

    def __init__(self, span):
        self.span = span

    def __enter__(self):
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.record_exception(exc_val)
        self.span.end()


class _NoopSpan:
    """No-op span when telemetry is disabled."""

    def __enter__(self):
        return None

    def __exit__(self, *args):
        pass


# Initialize on import
init_telemetry()
