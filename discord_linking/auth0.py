from flask import Blueprint, redirect, session, url_for
from sqlalchemy.exc import IntegrityError

from .database import User, db
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

    # Create the user if they don't already exist
    user = User(id=token["userinfo"]["sub"])
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        pass

    session["id"] = user.id
    return redirect(url_for("index"))
