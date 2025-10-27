"""
OpenTelemetry tracing setup
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.infrastructure.config.settings import settings


def setup_tracing(app) -> None:
    """
    Setup OpenTelemetry tracing

    Args:
        app: FastAPI application instance
    """
    if not settings.ENABLE_TRACING:
        return

    resource = Resource.create({
        "service.name": settings.SERVICE_NAME,
        "service.version": settings.SERVICE_VERSION,
        "deployment.environment": settings.ENVIRONMENT
    })

    provider = TracerProvider(resource=resource)

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=True
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()


def get_tracer():
    """Get tracer instance"""
    return trace.get_tracer(__name__)
