import requests
from flask import current_app
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def can_link(id: str) -> bool:
    """
    Check if the participant is allowed to link their account
    :return: whether the participant can link
    """
    with tracer.start_as_current_span("can-link"):
        base = current_app.config["APPLICATION_PORTAL_URL"]
        response = requests.get(base + f"/discord/can-link?id={id}")
        response.raise_for_status()

        return response.json().get("status", False)
