from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import profiles

db = SQLAlchemy()
migrate = Migrate(db=db)


def init(app):
    db.init_app(app)
    migrate.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(64), primary_key=True)

    agreed_to_rules = db.Column(db.Boolean, nullable=False, default=False)
    agreed_to_code_of_conduct = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def agreed(self):
        return self.agreed_to_rules and self.agreed_to_code_of_conduct

    @property
    def profile(self):
        return profiles.fetch(self.id)


class Link(db.Model):
    __tablename__ = "links"

    user = db.relationship("User", backref=db.backref("link", uselist=False))
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), primary_key=True)

    id = db.Column(db.String(64), nullable=False)

    username = db.Column(db.String, nullable=False)
    discriminator = db.Column(db.String(4), nullable=False)

    avatar = db.Column(db.String(64), nullable=True)

    @property
    def profile_url(self):
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"

        return "https://wafflehacks-static.s3.us-west-2.amazonaws.com/third-party/discord.png"
