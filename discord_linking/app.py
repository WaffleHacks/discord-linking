from flask import Flask, g, render_template, request, session, url_for

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
    # Ignore static resources
    if request.path.startswith("/static") or request.path == "/favicon.ico":
        return

    # Handle initial login
    if request.path != url_for("auth0.callback") and "id" not in session:
        session["auth0:login"] = True
        return auth0.login()

    # Get the user's profile
    g.user = User.query.filter_by(id=session["id"]).first()

    # Handle linking
    if request.path != url_for("discord.callback") and g.user.link is None:
        session["discord:login"] = True
        return discord.login()


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(*_):
    return render_template("404.html"), 404
