def test_admin_status_returns_200(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "admin panel active"


def test_admin_ping_default_host(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    body = res.get_json()
    assert "result" in body
    assert body["host"] == "localhost"


def test_admin_ping_custom_host(client):
    res = client.get("/api/admin/ping?host=127.0.0.1")
    assert res.status_code == 200
    body = res.get_json()
    assert body["host"] == "127.0.0.1"
