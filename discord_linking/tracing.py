from os import environ
from sys import stderr

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
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
enabled = (
    otel_enable == "yes"
    or otel_enable == "y"
    or otel_enable == "true"
    or otel_enable == "t"
)


def init(app, db):
    if enabled:
        # Select the exporter
        if app.debug:
            print("OpenTelemetry: Jaeger", file=stderr)
            exporter = JaegerExporter(agent_port=3531)
        else:
            print("OpenTelemetry: OTLP", file=stderr)
            exporter = OTLPSpanExporter()

        # Setup the exporter
        processor = BatchSpanProcessor(exporter)
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
        print(" * OpenTelemetry: disabled", file=stderr)
