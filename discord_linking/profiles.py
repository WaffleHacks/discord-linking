from dataclasses import dataclass

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from flask_caching import Cache

auth = BotoAWSRequestsAuth("api.id.wafflehacks.org", "us-west-2", "execute-api")
cache = Cache()


def init(app):
    cache.init_app(app)


@dataclass
class Profile:
    first_name: str
    last_name: str
    email: str

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


@cache.memoize(timeout=30 * 24 * 60 * 60)  # Cache for a month
def fetch(user: str) -> Profile:
    """
    Fetch a user's profile from the profiles service
    :param user: the user's ID
    :return: a profile for the user
    """
    response = requests.get(f"https://api.id.wafflehacks.org/manage/{user}", auth=auth)
    response.raise_for_status()

    raw = response.json()
    return Profile(
        first_name=raw["firstName"],
        last_name=raw["lastName"],
        email=raw["email"],
    )


def invalidate(user: str):
    """
    Invalidate a user's cached profile
    :param user: the user's ID
    """
    cache.delete_memoized(fetch, user)
