from flask import Flask, render_template

from . import database, oauth

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
oauth.init(app)


@app.get("/")
def index():
    return render_template("index.html")
