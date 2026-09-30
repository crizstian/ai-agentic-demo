def test_admin_status_returns_200(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "admin panel active"


def test_admin_ping_returns_result(client):
    res = client.get("/api/admin/ping?host=localhost")
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data
    assert data["host"] == "localhost"
