from urllib.parse import urlparse

from flask import Blueprint, abort, jsonify, request

from .database import User

app = Blueprint("internal", __name__, template_folder="templates")


@app.before_request
def before_request():
    url = urlparse(request.host_url)
    if not url.hostname.endswith("wafflemaker.internal"):
        abort(401)


@app.get("/linked")
def linked():
    user = User.query.filter_by(id=request.args.get("id")).first()
    if user:
        status = user.agreed and user.link is not None
    else:
        status = False

    return jsonify({"linked": status})


@app.errorhandler(401)
def unauthorized(*_):
    return jsonify({"message": "unauthorized"}), 401
