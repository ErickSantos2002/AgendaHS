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

    @app.route("/health")
    def health():
        return "ok"

    return app
