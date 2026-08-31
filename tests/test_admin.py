def test_admin_ping_returns_200(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    body = res.get_json()
    assert "result" in body


def test_admin_ping_with_host_param(client):
    res = client.get("/api/admin/ping?host=127.0.0.1")
    assert res.status_code == 200
    body = res.get_json()
    assert body["host"] == "127.0.0.1"
    assert "127.0.0.1" in body["result"]


def test_command_injection_in_ping(client):
    """Verify command injection vulnerability -- user input reaches shell output."""
    res = client.get("/api/admin/ping?host=127.0.0.1;echo+injected")
    assert res.status_code == 200
    body = res.get_json()
    assert "injected" in body["result"]


def test_admin_ping_default(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    body = res.get_json()
    assert body["host"] == "localhost"
    assert "localhost" in body["result"]


def test_admin_blueprint_registered(client):
    assert "admin" in client.application.blueprints
