from flask import Flask

from . import database, oauth

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
oauth.init(app)
