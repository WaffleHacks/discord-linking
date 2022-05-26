from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, g, redirect, render_template, url_for
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
    return registry.discord.authorize_redirect(
        url_for(
            "discord.callback",
            _external=True,
            _scheme="http" if current_app.debug else "https",
        )
    )


@app.get("/callback")
def callback():
    # Complete the login flow
    with tracer.start_as_current_span("token-exchange"):
        try:
            token = registry.discord.authorize_access_token()
        except OAuthError:
            return render_template(
                "error.html",
                message=(
                    "It looks like you cancelled the linking process. To access our Discord "
                    "community, you must allow WaffleHacks to view your Discord username and avatar."
                ),
                title="Operation cancelled",
            )

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
