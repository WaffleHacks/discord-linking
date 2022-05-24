import base64
import json

from flask import Blueprint, redirect, session, url_for
from sqlalchemy.exc import IntegrityError

from .database import Link, User, db
from .oauth import registry

app = Blueprint("auth0", __name__, template_folder="templates")


def login():
    """
    Initiate the login flow for Auth0
    :return: redirect to Auth0
    """
    return registry.auth0.authorize_redirect(
        url_for("auth0.callback", _external=True),
        audience="https://discord.wafflehacks.org",
    )


@app.get("/callback")
def callback():
    # Complete the login flow
    token = registry.auth0.authorize_access_token()
    userinfo = token["userinfo"]

    # Only allow participants to link their accounts
    if not is_participant(token["access_token"]):
        session["error"] = (
            "Only participants can link their Discord accounts. "
            "Please DM an organizer be admitted into the Discord."
        )
        return redirect(url_for("error"))

    user = User(id=userinfo["sub"])

    # Determine if the participant can be pre-emptively linked since they signed in with Discord
    if user.id.startswith("oauth2|discord|"):
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
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        pass

    session["id"] = user.id
    return redirect(url_for("index"))


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
    payload = decode_jwt(raw)
    permissions = payload.get("permissions")
    if type(permissions) == list:
        return "participant" in permissions
    elif type(permissions) == str:
        return permissions == "participant"
    else:
        return True
