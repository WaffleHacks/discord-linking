import json
from contextlib import asynccontextmanager

from flask import current_app, g
from nats import NATS
from nats.js import JetStreamContext
from nats.js.api import RetentionPolicy, StorageType
from nats.js.errors import NotFoundError
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

STREAM_NAME = "discord-linking"

__client = NATS()
__propagator = TraceContextTextMapPropagator()


def init(app):
    create_stream(app)


async def __connect(app=current_app) -> JetStreamContext:
    """
    Handle automatically connecting to NATS when needed
    """
    if not __client.is_connected and not __client.is_reconnecting:
        await __client.connect(servers=[app.config.get("NATS_URL")])

    return __client.jetstream()


@asynccontextmanager
async def __connection(app=current_app):
    """
    Get a NATS connection
    """
    client = NATS()
    await client.connect(servers=[app.config["NATS_URL"]])

    try:
        yield client.jetstream()
    finally:
        await client.close()


def create_stream(app=current_app):
    """
    Create a new stream if it doesn't already exist
    """

    async def inner():
        async with __connection(app) as jetstream:
            try:
                await jetstream.stream_info(STREAM_NAME)
            except NotFoundError:
                await jetstream.add_stream(
                    name=STREAM_NAME,
                    subjects=[f"{STREAM_NAME}.*"],
                    description="for the Discord linking service",
                    storage=StorageType.FILE,
                    retention=RetentionPolicy.LIMITS,
                    num_replicas=1,
                    max_age=60 * 60 * 24 * 180,  # 6 months
                )

    app.ensure_sync(inner)()


def publish(event: str):
    """
    Publish a message to a particular subject
    """

    async def inner():
        async with __connection() as jetstream:
            # Inject tracing
            headers = {}
            __propagator.inject(headers)

            # Encode the body
            body = {"id": g.user.id}
            encoded = json.dumps(body).encode("utf-8")

            await jetstream.publish(f"{STREAM_NAME}.{event}", encoded, headers=headers)

    current_app.ensure_sync(inner)()
