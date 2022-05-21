from flask import Flask, render_template, session

from . import auth0, database, oauth

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
oauth.init(app)

app.register_blueprint(auth0.app, url_prefix="/auth0")


@app.before_request
def require_login():
    print(session)

    if "auth0:login" in session:
        del session["auth0:login"]
        return

    if "id" not in session:
        session["auth0:login"] = True
        return auth0.login()


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(*_):
    return render_template("404.html"), 404
