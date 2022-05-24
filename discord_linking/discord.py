import requests
from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, g, redirect, session, url_for
from opentelemetry import trace

from .database import Link, db
from .oauth import registry

app = Blueprint("discord", __name__, template_folder="templates")
tracer = trace.get_tracer(__name__)


def login():
    """
    Initiate the linking flow for Discord
    :return: redirect to Discord
    """
    # Only redirect if participant is allowed to link their account
    if can_link():
        return registry.discord.authorize_redirect(
            url_for(
                "discord.callback",
                _external=True,
                _scheme="http" if current_app.debug else "https",
            )
        )
    else:
        session["error"] = (
            "Before you can join the community Discord, your application needs to be accepted. This should happen "
            "within a week of applying.<br/><br/>If you haven't applied yet, go to <a "
            'href="https://apply.wafflehacks.org" class="text-blue-500 underline hover:no-underline">'
            "apply.wafflehacks.org</a> to get started. It'll only take 5-10 minutes to complete.<br/><br/>If you think "
            'you received this in error, please send us an email at <a href="" class="text-blue-500 underline '
            'hover:no-underline"></a>.'
        )
        session["error:title"] = "You can't do that yet"
        session["error:try-again"] = False
        return redirect(url_for("error"))


@app.get("/callback")
def callback():
    # Complete the login flow
    with tracer.start_as_current_span("token-exchange"):
        try:
            token = registry.discord.authorize_access_token()
        except OAuthError:
            session["error"] = (
                "It looks like you cancelled the linking process. To access our Discord "
                "community, you must allow WaffleHacks to view your Discord username and avatar."
            )
            session["error:title"] = "Operation cancelled"
            return redirect(url_for("error"))

    # Get the user's info
    user_info = registry.discord.userinfo(token=token)

    # Create the account link
    with tracer.start_as_current_span("complete-link"):
        link = Link(
            user=g.user,
            id=user_info["id"],
            username=user_info["username"],
            discriminator=user_info["discriminator"],
            avatar=user_info["avatar"],
        )
        db.session.add(link)
        db.session.commit()

    return redirect(url_for("index"))


def can_link():
    """
    Check if the participant is allowed to link their account
    :return: whether the participant can link
    """
    with tracer.start_as_current_span("can-link"):
        base = current_app.config["APPLICATION_PORTAL_URL"]
        response = requests.get(base + f"/discord/can-link?id={g.user.id}")
        response.raise_for_status()

        return response.json().get("status", False)
