from flask import Flask, jsonify, redirect, render_template, request

app = Flask(__name__)

state = {}


@app.get("/")
def index():
    return render_template("index.html", state=state)


@app.post("/add")
def add():
    user = request.form.get("id")
    if user:
        state[user] = True

    return redirect("/")


@app.get("/<user>/toggle")
def toggle(user):
    state[user] = not state.get(user, False)
    return redirect("/")


@app.get("/<user>/delete")
def delete(user):
    del state[user]
    return redirect("/")


@app.get("/discord/can-link")
def can_link():
    user = request.args.get("id")
    if user is None:
        return jsonify({"success": False, "reason": "invalid request"}), 422

    status = state.setdefault(user, False)
    return jsonify({"status": status})
