from os import environ

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

otel_enable = environ.get("OTEL_ENABLE", "no").lower()
should_enable = (
    otel_enable == "yes"
    or otel_enable == "y"
    or otel_enable == "true"
    or otel_enable == "t"
)


def init(app, db):
    if should_enable:
        print(" * OpenTelemetry: enabled")

        # Setup the exporter
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider = TracerProvider()
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)

        # Setup default instrumentation
        BotocoreInstrumentor().instrument()
        FlaskInstrumentor().instrument_app(app)
        Jinja2Instrumentor().instrument()
        RedisInstrumentor().instrument()
        RequestsInstrumentor().instrument()

        with app.app_context():
            SQLAlchemyInstrumentor().instrument(engine=db.engine)
    else:
        print(" * OpenTelemetry: disabled")
