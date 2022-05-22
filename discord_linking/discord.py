from flask import Blueprint, g, redirect, url_for

from .database import Link, db
from .oauth import registry

app = Blueprint("discord", __name__, template_folder="templates")


def login():
    """
    Initiate the linking flow for Discord
    :return: redirect to Discord
    """
    return registry.discord.authorize_redirect(
        url_for("discord.callback", _external=True)
    )


@app.get("/callback")
def callback():
    # Complete the login flow
    token = registry.discord.authorize_access_token()

    # Get the user's info
    user_info = registry.discord.userinfo(token=token)

    # Create the account link
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
