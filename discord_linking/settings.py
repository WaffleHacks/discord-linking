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
