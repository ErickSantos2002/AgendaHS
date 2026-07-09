from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, session, current_app
)

bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    erro = False
    if request.method == "POST":
        if request.form.get("senha") == current_app.config["SENHA"]:
            session["logado"] = True
            return redirect(url_for("eventos.painel"))
        erro = True
    return render_template("login.html", erro=erro)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
