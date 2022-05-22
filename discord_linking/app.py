from flask import Flask, g, render_template, session

from . import auth0, database, discord, oauth
from .database import User

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
oauth.init(app)

app.register_blueprint(auth0.app, url_prefix="/auth0")
app.register_blueprint(discord.app, url_prefix="/discord")


@app.before_request
def require_login():
    # Handle initial login
    if "auth0:login" in session:
        del session["auth0:login"]
        return
    elif "id" not in session:
        session["auth0:login"] = True
        return auth0.login()

    # Get the user's profile
    g.user = User.query.filter_by(id=session["id"]).first()

    # Handle linking
    if "discord:login" in session:
        del session["discord:login"]
        return
    elif g.user.link is None:
        session["discord:login"] = True
        return discord.login()


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(*_):
    return render_template("404.html"), 404
