import os

_initialized = False


def init_tracing(app):
    """Initialize OpenTelemetry distributed tracing with lazy loading.

    Instruments Flask (incoming) and requests/httpx (outgoing) to propagate
    W3C traceparent across the AI agent call chain. Exports spans to
    Traceable's TPA via zipkin so they appear alongside nginx-level traces.
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    enabled = os.environ.get("OTEL_ENABLED", "true").lower() in ("1", "true", "on")
    if not enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.zipkin.json import ZipkinExporter
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        service_name = os.environ.get("OTEL_SERVICE_NAME", "DemoBank-AI-Agent")
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        zipkin_endpoint = os.environ.get(
            "OTEL_EXPORTER_ZIPKIN_ENDPOINT",
            "http://traceable-agent:5442/api/v2/spans",
        )
        try:
            exporter = ZipkinExporter(endpoint=zipkin_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception as exc:
            print(f"[OTEL] Zipkin exporter failed ({exc}), traces will propagate but not export")

        trace.set_tracer_provider(provider)

        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

        try:
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

            HTTPXClientInstrumentor().instrument()
        except Exception:
            pass

        print(f"[OTEL] Distributed tracing enabled — service={service_name}")
    except Exception as exc:
        print(f"[OTEL] Init failed ({exc}), app continues without tracing")
