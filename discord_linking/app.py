import traceback

from flask import Flask, g, redirect, render_template, request, session, url_for
from opentelemetry import trace

from . import auth0, database, dependencies, discord, internal, oauth, tracing
from .database import User, db

app = Flask(__name__)
app.config.from_object("discord_linking.settings")

database.init(app)
dependencies.init(app)
oauth.init(app)
tracing.init(app, db)

app.register_blueprint(auth0.app, url_prefix="/auth0")
app.register_blueprint(discord.app, url_prefix="/discord")
app.register_blueprint(internal.app, url_prefix="/internal")

tracer = trace.get_tracer(__name__)


@app.before_request
def require_login():
    # Ignore static resources and errors
    if (
        request.path.startswith("/static")
        or request.path.startswith("/internal")
        or request.path == "/favicon.ico"
        or request.path == url_for("error")
    ):
        return

    # Handle initial login
    if request.path == url_for("auth0.callback"):
        return
    elif "id" not in session:
        session["auth0:login"] = True
        return auth0.login()

    # Get the user's profile
    g.user = User.query.filter_by(id=session["id"]).first()
    trace.get_current_span().set_attribute("user.id", g.user.id)

    # Handle linking
    if request.path != url_for("discord.callback") and g.user.link is None:
        session["discord:login"] = True
        return discord.login()

    # Only show status page if already linked
    if not g.user.agreed and request.path != url_for("edit"):
        return redirect(url_for("edit"))


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        with tracer.start_as_current_span("update"):
            g.user.agreed_to_rules = request.form.get("rules") == "on"
            g.user.agreed_to_code_of_conduct = (
                request.form.get("code-of-conduct") == "on"
            )
            db.session.commit()

        if g.user.agreed:
            return redirect(url_for("index"))
        else:
            return render_template(
                "edit.html",
                error="You must accept the rules and code of conduct to access the WaffleHacks Discord",
            )

    return render_template("edit.html")


@app.get("/error")
def error():
    if "error" not in session:
        return redirect(url_for("index"))

    return render_template(
        "error.html",
        error=session.pop("error"),
        title=session.pop("error:title", None),
        try_again=session.pop("error:try-again", True),
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/unlink")
def unlink():
    with tracer.start_as_current_span("delete"):
        if g.user.link:
            db.session.delete(g.user.link)
            db.session.commit()

    return redirect(url_for("index"))


@app.get("/refresh")
def refresh():
    with tracer.start_as_current_span("invalidate-cache"):
        dependencies.invalidate_profile(g.user.id)
    return redirect(url_for("edit"))


@app.errorhandler(404)
def not_found(*_):
    return render_template("404.html"), 404


@app.errorhandler(Exception)
def internal_server(*_):
    if not tracing.enabled:
        traceback.print_exc()
    return render_template("500.html"), 500
