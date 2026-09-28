def test_admin_status(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "admin panel active"


def test_admin_ping_default(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data
    assert "host" in data
    assert data["host"] == "localhost"


def test_admin_ping_custom_host(client):
    res = client.get("/api/admin/ping?host=example")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "example"
