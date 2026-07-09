from app.db import get_db


def test_tabelas_existem(app):
    with app.app_context():
        db = get_db()
        nomes = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {"evento", "evento_data", "participante", "participante_data"} <= nomes


def test_foreign_keys_ativo(app):
    with app.app_context():
        db = get_db()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
