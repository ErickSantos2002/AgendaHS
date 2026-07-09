import os
from flask import Flask


def create_app(config=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = os.environ.get("AGENDAHS_DB", "/app/data/eventos.db")
    app.config["SENHA"] = os.environ.get("AGENDAHS_SENHA")
    app.config["SECRET_KEY"] = os.environ.get("AGENDAHS_SECRET_KEY", "dev-inseguro")
    if config:
        app.config.update(config)

    @app.route("/health")
    def health():
        return "ok"

    return app
