from app.db import get_db


def _criar_evento_com_datas(client, app):
    client.post("/login", data={"senha": "segredo"})
    client.post("/eventos", data={
        "titulo": "Reunião", "descricao": "",
        "data": ["2026-08-05", "2026-08-06"], "horario": ["", ""],
    })
    with app.app_context():
        db = get_db()
        slug = db.execute("SELECT id FROM evento").fetchone()["id"]
        datas = db.execute(
            "SELECT id FROM evento_data WHERE evento_id=? ORDER BY id", (slug,)
        ).fetchall()
    return slug, [d["id"] for d in datas]


def test_form_publico_abre_sem_login(client, app):
    slug, _ = _criar_evento_com_datas(client, app)
    c2 = app.test_client()  # sem sessão
    resp = c2.get(f"/e/{slug}")
    assert resp.status_code == 200
    assert "Reunião" in resp.get_data(as_text=True)


def test_form_publico_slug_inexistente_404(client):
    resp = client.get("/e/naoexiste")
    assert resp.status_code == 404


def test_responder_persiste(client, app):
    slug, datas = _criar_evento_com_datas(client, app)
    resp = client.post(f"/e/{slug}/responder", data={
        "nome": "  João  ", "datas": [str(datas[0])],
    })
    assert resp.status_code == 200
    with app.app_context():
        db = get_db()
        p = db.execute("SELECT * FROM participante WHERE evento_id=?", (slug,)).fetchone()
        assert p["nome"] == "João"
        n = db.execute(
            "SELECT COUNT(*) c FROM participante_data WHERE participante_id=?", (p["id"],)
        ).fetchone()["c"]
        assert n == 1


def test_responder_sem_nome_erro(client, app):
    slug, datas = _criar_evento_com_datas(client, app)
    resp = client.post(f"/e/{slug}/responder", data={"nome": "", "datas": [str(datas[0])]})
    assert "nome" in resp.get_data(as_text=True).lower()


def test_responder_zero_datas_permitido(client, app):
    slug, _ = _criar_evento_com_datas(client, app)
    resp = client.post(f"/e/{slug}/responder", data={"nome": "Ana"})
    assert resp.status_code == 200
    with app.app_context():
        db = get_db()
        p = db.execute("SELECT * FROM participante WHERE nome='Ana'").fetchone()
        assert p is not None
        n = db.execute(
            "SELECT COUNT(*) c FROM participante_data WHERE participante_id=?", (p["id"],)
        ).fetchone()["c"]
        assert n == 0


def test_responder_mesmo_nome_atualiza(client, app):
    slug, datas = _criar_evento_com_datas(client, app)
    client.post(f"/e/{slug}/responder", data={"nome": "Bia", "datas": [str(datas[0])]})
    client.post(f"/e/{slug}/responder", data={"nome": "bia", "datas": [str(datas[1])]})
    with app.app_context():
        db = get_db()
        n_p = db.execute(
            "SELECT COUNT(*) c FROM participante WHERE evento_id=?", (slug,)
        ).fetchone()["c"]
        assert n_p == 1
        p = db.execute("SELECT * FROM participante WHERE evento_id=?", (slug,)).fetchone()
        disp = db.execute(
            "SELECT evento_data_id FROM participante_data WHERE participante_id=?", (p["id"],)
        ).fetchall()
        assert [r["evento_data_id"] for r in disp] == [datas[1]]
