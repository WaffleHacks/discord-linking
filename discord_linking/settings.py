from os import environ
from dotenv import load_dotenv

load_dotenv()

raw_debug = (environ.get("DEBUG") or "no").lower()
DEBUG = (
    raw_debug == "yes"
    or raw_debug == "true"
    or raw_debug == "y"
    or raw_debug == "t"
    or raw_debug == "1"
)
