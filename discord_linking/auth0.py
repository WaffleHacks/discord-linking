import base64
import json

from flask import Blueprint, current_app, redirect, render_template, session, url_for
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError

from .database import Link, User, db
from .oauth import registry

app = Blueprint("auth0", __name__, template_folder="templates")
tracer = trace.get_tracer(__name__)


def login():
    """
    Initiate the login flow for Auth0
    :return: redirect to Auth0
    """
    return registry.auth0.authorize_redirect(
        url_for(
            "auth0.callback",
            _external=True,
            _scheme="http" if current_app.debug else "https",
        ),
        audience="https://discord.wafflehacks.org",
    )


@app.get("/callback")
def callback():
    # Complete the login flow
    with tracer.start_as_current_span("token-exchange"):
        token = registry.auth0.authorize_access_token()
        userinfo = token["userinfo"]

    # Only allow participants to link their accounts
    with tracer.start_as_current_span("can-start-linking"):
        if not is_participant(token["access_token"]):
            return render_template(
                "error.html",
                message=(
                    "Only participants can link their Discord accounts. "
                    "Please DM an organizer be admitted into the Discord."
                ),
                disable_try_again=True,
            )

    user = User(id=userinfo["sub"])

    # Determine if the participant can be pre-emptively linked since they signed in with Discord
    with tracer.start_as_current_span("pre-emptive-link"):
        if user.id.startswith("oauth2|discord|") and user.can_link:
            # Get the username and discriminator from the user info
            # The `nickname` property will ALWAYS have the full username in the format <username>#<discriminator>
            [username, discriminator] = userinfo["nickname"].split("#")

            # Get the user's profile picture
            if "cdn.discordapp.com" in userinfo["picture"]:
                avatar_parts = userinfo["picture"].split("/")
                avatar = avatar_parts[-1].removesuffix(".png")
            else:
                avatar = None

            link = Link(
                user=user,
                id=user.id.removeprefix("oauth2|discord|"),
                username=username,
                discriminator=discriminator,
                avatar=avatar,
            )
            db.session.add(link)

    # Create the user if they don't already exist and optionally add the link
    with tracer.start_as_current_span("save"):
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            pass

    session["id"] = user.id
    return redirect(url_for("edit"))


def decode_jwt(raw):
    """
    Decode the payload of a JWT without verifying it
    :param raw: the JWT
    :return: a payload dictionary
    """
    [_, payload, _] = raw.split(".", 2)

    padding_needed = len(payload) % 4
    if padding_needed > 0:
        payload += "=" * (4 - padding_needed)

    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)


def is_participant(raw):
    """
    Determine if a given token belongs to a participant
    :param raw: the raw JWT string
    :return: whether the token owner is a participant
    """
    with tracer.start_as_current_span("is-participant") as span:
        with tracer.start_as_current_span("token-decode"):
            payload = decode_jwt(raw)

        permissions = payload.get("permissions")
        span.set_attribute("permissions", permissions)
        if type(permissions) == list:
            return "can-link" in permissions
        elif type(permissions) == str:
            return permissions == "participant"
        else:
            return True
