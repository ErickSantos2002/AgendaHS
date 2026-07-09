from app.db import get_db


def _login(client):
    client.post("/login", data={"senha": "segredo"})


def test_criar_evento_persiste(client, app):
    _login(client)
    resp = client.post("/eventos", data={
        "titulo": "Reunião",
        "descricao": "pauta X",
        "data": ["2026-08-05", "2026-08-06"],
        "horario": ["09:00", ""],
    }, follow_redirects=False)
    assert resp.status_code == 302
    with app.app_context():
        db = get_db()
        ev = db.execute("SELECT * FROM evento").fetchone()
        assert ev["titulo"] == "Reunião"
        n = db.execute(
            "SELECT COUNT(*) c FROM evento_data WHERE evento_id=?", (ev["id"],)
        ).fetchone()["c"]
        assert n == 2


def test_painel_lista_evento(client):
    _login(client)
    client.post("/eventos", data={
        "titulo": "Churrasco", "descricao": "",
        "data": ["2026-08-10"], "horario": [""],
    })
    resp = client.get("/painel")
    assert "Churrasco" in resp.get_data(as_text=True)


def test_criar_exige_login(client):
    resp = client.post("/eventos", data={"titulo": "X"})
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_criar_exige_titulo(client):
    _login(client)
    resp = client.post("/eventos", data={
        "titulo": "", "descricao": "",
        "data": ["2026-08-10"], "horario": [""],
    })
    assert "título" in resp.get_data(as_text=True).lower()


def test_detalhe_mostra_contagem(client, app):
    _login(client)
    client.post("/eventos", data={
        "titulo": "Jogo", "descricao": "",
        "data": ["2026-08-01", "2026-08-02"], "horario": ["", ""],
    })
    with app.app_context():
        db = get_db()
        slug = db.execute("SELECT id FROM evento").fetchone()["id"]
        datas = db.execute(
            "SELECT id FROM evento_data WHERE evento_id=? ORDER BY id", (slug,)
        ).fetchall()
    client.post(f"/e/{slug}/responder", data={
        "nome": "João", "datas": [str(datas[0]["id"]), str(datas[1]["id"])],
    })
    client.post(f"/e/{slug}/responder", data={
        "nome": "Maria", "datas": [str(datas[0]["id"])],
    })
    resp = client.get(f"/eventos/{slug}")
    texto = resp.get_data(as_text=True)
    assert "João" in texto and "Maria" in texto


def test_detalhe_evento_inexistente_404(client):
    _login(client)
    resp = client.get("/eventos/naoexiste")
    assert resp.status_code == 404


def test_calendario_marca_dia_do_evento(client):
    _login(client)
    client.post("/eventos", data={
        "titulo": "Festa", "descricao": "",
        "data": ["2026-08-15"], "horario": [""],
    })
    resp = client.get("/painel?ano=2026&mes=8")
    texto = resp.get_data(as_text=True)
    assert "tem-evento" in texto
    assert "Festa" in texto


def test_404_pagina_amigavel(client):
    resp = client.get("/rota/que/nao/existe")
    assert resp.status_code == 404
    assert "não encontrad" in resp.get_data(as_text=True).lower()
