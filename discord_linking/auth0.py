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
    url = url_for("auth0.callback", _external=True)
    return registry.auth0.authorize_redirect(url)


@app.get("/callback")
def callback():
    # Complete the login flow
    token = registry.auth0.authorize_access_token()
    userinfo = token["userinfo"]

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
