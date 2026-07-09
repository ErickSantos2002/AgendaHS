def test_login_senha_certa(client):
    resp = client.post("/login", data={"senha": "segredo"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "senha incorreta" not in resp.get_data(as_text=True).lower()


def test_login_senha_errada(client):
    resp = client.post("/login", data={"senha": "errada"})
    assert "senha incorreta" in resp.get_data(as_text=True).lower()


def test_rota_protegida_redireciona(client):
    resp = client.get("/painel")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_rota_protegida_ok_apos_login(client):
    client.post("/login", data={"senha": "segredo"})
    resp = client.get("/painel")
    assert resp.status_code == 200
