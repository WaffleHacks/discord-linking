from os import environ

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(OTLPSpanExporter())

provider = TracerProvider()
provider.add_span_processor(processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


def init(app, db):
    if environ.get("OTEL_SERVICE_NAME") is not None:
        BotocoreInstrumentor().instrument()
        FlaskInstrumentor().instrument_app(app)
        Jinja2Instrumentor().instrument()
        RequestsInstrumentor().instrument()

        with app.app_context():
            SQLAlchemyInstrumentor().instrument(engine=db.engine)
