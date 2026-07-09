import sqlite3
from flask import g, current_app

SCHEMA = """
CREATE TABLE IF NOT EXISTS evento (
    id         TEXT PRIMARY KEY,
    titulo     TEXT NOT NULL,
    descricao  TEXT,
    criado_em  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evento_data (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id  TEXT NOT NULL REFERENCES evento(id) ON DELETE CASCADE,
    data       TEXT NOT NULL,
    horario    TEXT
);
CREATE TABLE IF NOT EXISTS participante (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id  TEXT NOT NULL REFERENCES evento(id) ON DELETE CASCADE,
    nome       TEXT NOT NULL,
    criado_em  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS participante_data (
    participante_id INTEGER NOT NULL REFERENCES participante(id) ON DELETE CASCADE,
    evento_data_id  INTEGER NOT NULL REFERENCES evento_data(id) ON DELETE CASCADE,
    PRIMARY KEY (participante_id, evento_data_id)
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_schema(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    init_schema(app)
