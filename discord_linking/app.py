from flask import Flask, render_template

from . import database, oauth

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
oauth.init(app)


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(*_):
    return render_template("404.html"), 404
