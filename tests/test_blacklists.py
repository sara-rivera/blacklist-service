

# ---------------------------------------------------------------- GET /ping
def test_ping_responde_ok(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


# ---------------------------------------------------------------- POST /blacklists
def test_agregar_email_exitoso(client, headers, payload):
    resp = client.post("/blacklists", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["email"] == "bloqueado@test.com"
    assert data["blocked_reason"] == "Fraude"


def test_agregar_email_sin_token(client, payload):
    resp = client.post("/blacklists", json=payload)
    assert resp.status_code == 401


def test_agregar_email_con_token_invalido(client, payload):
    resp = client.post("/blacklists", json=payload,
                       headers={"Authorization": "Bearer token-falso"})
    assert resp.status_code == 401


def test_agregar_email_invalido(client, headers, payload):
    payload["email"] = "no-es-un-email"
    resp = client.post("/blacklists", json=payload, headers=headers)
    assert resp.status_code == 400


def test_agregar_sin_app_uuid(client, headers):
    resp = client.post("/blacklists", json={"email": "x@test.com"}, headers=headers)
    assert resp.status_code == 400


def test_agregar_email_duplicado(client, headers, payload):
    client.post("/blacklists", json=payload, headers=headers)
    resp = client.post("/blacklists", json=payload, headers=headers)
    assert resp.status_code == 409


# ---------------------------------------------------------------- GET /blacklists/<email>
def test_consultar_email_en_lista_negra(client, headers, payload):
    client.post("/blacklists", json=payload, headers=headers)
    resp = client.get("/blacklists/bloqueado@test.com", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["is_blacklisted"] is True
    assert body["blocked_reason"] == "Fraude"


def test_consultar_email_no_bloqueado(client, headers):
    resp = client.get("/blacklists/libre@test.com", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["is_blacklisted"] is False


def test_consultar_email_sin_token(client):
    resp = client.get("/blacklists/libre@test.com")
    assert resp.status_code == 401
