from flask import Flask

from .database import init as init_database

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

init_database(app)
