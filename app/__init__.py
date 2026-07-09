import os
from flask import Flask


def create_app(config=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = os.environ.get("AGENDAHS_DB", "/app/data/eventos.db")
    app.config["SENHA"] = os.environ.get("AGENDAHS_SENHA")
    app.config["SECRET_KEY"] = os.environ.get("AGENDAHS_SECRET_KEY", "dev-inseguro")
    if config:
        app.config.update(config)

    os.makedirs(os.path.dirname(os.path.abspath(app.config["DB_PATH"])), exist_ok=True)

    from . import db
    db.init_app(app)

    if not app.config.get("SENHA"):
        raise RuntimeError(
            "AGENDAHS_SENHA não configurada — painel ficaria sem proteção"
        )

    from . import auth, eventos, publico
    app.register_blueprint(auth.bp)
    app.register_blueprint(eventos.bp)
    app.register_blueprint(publico.bp)

    from datetime import date as _date
    _DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    @app.template_filter("data_br")
    def data_br(iso):
        try:
            d = _date.fromisoformat(iso)
        except (ValueError, TypeError):
            return iso
        return f"{_DIAS[d.weekday()]} {d.day:02d}/{d.month:02d}"

    from flask import render_template

    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("404.html"), 404

    @app.route("/health")
    def health():
        return "ok"

    return app
