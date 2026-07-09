import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import SpanKind


# OpenTelemetry Configuration
class OpenTelemetryConfig:
    def __init__(self):
        self.service_name = os.getenv("OTEL_SERVICE_NAME", "convocatorias-backend")
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector.istio-system.svc.cluster.local:4317"
        )
        self.sampling_rate = float(os.getenv("OTEL_SAMPLING_RATE", "0.1"))

    def setup(self):
        resource = Resource.create(
            attributes={
                ResourceAttributes.SERVICE_NAME: self.service_name,
                ResourceAttributes.SERVICE_VERSION: "1.0.0",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
                "k8s.namespace": "convocatorias",
            }
        )

        # Tracing with dynamic sampling
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self.otlp_endpoint, insecure=True),
                max_export_batch_size=500,
            )
        )
        trace.set_tracer_provider(tracer_provider)

        # Metrics
        meter_provider = MeterProvider(resource=resource)
        metrics.set_meter_provider(meter_provider)

        # Auto-instrumentation
        RequestsInstrumentor().instrument()
        LoggingInstrumentor().instrument(set_logging_format=True)


# Initialize OTel
config = OpenTelemetryConfig()
config.setup()
tracer = trace.get_tracer("convocatorias.tracer")
meter = metrics.get_meter("convocatorias.meter")

# Metrics
convocatorias_counter = meter.create_counter(
    "convocatorias.created.total", description="Total convocatorias created"
)

errors_counter = meter.create_counter(
    "convocatorias.errors.total", description="Total errors in convocatorias service"
)

latency_histogram = meter.create_histogram(
    "convocatorias.duration.seconds", description="Latency of convocatoria operations"
)


# Decorators for instrumentation
def traced_endpoint(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name, kind=SpanKind.SERVER) as span:
                span.set_attribute("http.route", kwargs.get("title", "unknown"))
                try:
                    result = func(*args, **kwargs)
                    convocatorias_counter.add(1, {"status": "success"})
                    return result
                except Exception as e:
                    errors_counter.add(1, {"error": str(e)})
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator
