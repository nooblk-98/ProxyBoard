import functools
import hashlib
import os
import secrets

from flask import redirect, request, session, url_for

_SECRET_KEY = os.environ.get("UI_SECRET_KEY", secrets.token_hex(32))
_USERNAME = os.environ.get("UI_USERNAME", "admin")
_PASSWORD_HASH = os.environ.get("UI_PASSWORD_HASH", "")
_PASSWORD_RAW = os.environ.get("UI_PASSWORD", "")

AUTH_ENABLED = bool(_PASSWORD_HASH or _PASSWORD_RAW)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(username: str, password: str) -> bool:
    if username != _USERNAME:
        return False
    if _PASSWORD_HASH:
        return secrets.compare_digest(_hash(password), _PASSWORD_HASH)
    if _PASSWORD_RAW:
        return secrets.compare_digest(password, _PASSWORD_RAW)
    return False


def is_authenticated() -> bool:
    if not AUTH_ENABLED:
        return True
    return session.get("authenticated") is True


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def register_auth_routes(app):
    app.secret_key = _SECRET_KEY

    @app.route("/login", methods=["GET", "POST"])
    def login():
        from flask import render_template
        error = None
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if check_credentials(username, password):
                session["authenticated"] = True
                return redirect(url_for("dashboard"))
            error = "Invalid username or password."
        return render_template("login.html", error=error)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))
