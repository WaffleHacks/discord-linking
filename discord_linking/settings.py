from binascii import hexlify
from os import environ, urandom

from dotenv import load_dotenv

load_dotenv()

# Set the debug mode
raw_debug = (environ.get("DEBUG") or "no").lower()
DEBUG = (
    raw_debug == "yes"
    or raw_debug == "true"
    or raw_debug == "y"
    or raw_debug == "t"
    or raw_debug == "1"
)

# Cookie signing key
SECRET_KEY = environ.get("SECRET_KEY") or hexlify(urandom(32)).decode()

# Database configuration
SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "").replace(
    "postgres://", "postgresql://"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Auth0 configuration
AUTH0_CLIENT_ID = environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = environ.get("AUTH0_CLIENT_SECRET")

auth0_domain = environ.get("AUTH0_DOMAIN")
AUTH0_SERVER_METADATA_URL = f"https://{auth0_domain}/.well-known/openid-configuration"

# Discord configuration
DISCORD_CLIENT_ID = environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = environ.get("DISCORD_CLIENT_SECRET")

# Caching configuration
CACHE_TYPE = "RedisCache"
CACHE_KEY_PREFIX = "discord-linking:"
CACHE_REDIS_URL = environ.get("REDIS_URL")
