from unittest.mock import patch


@patch("app.routes.admin.subprocess.check_output")
def test_admin_ping_with_host(mock_subprocess, client):
    """GET /api/admin/ping?host=example.com returns result with host."""
    mock_subprocess.return_value = "Pinging: example.com"

    res = client.get("/api/admin/ping?host=example.com")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "example.com"
    assert "result" in data
    mock_subprocess.assert_called_once()


@patch("app.routes.admin.subprocess.check_output")
def test_admin_ping_default_localhost(mock_subprocess, client):
    """GET /api/admin/ping without host uses localhost."""
    mock_subprocess.return_value = "Pinging: localhost"

    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "localhost"
    mock_subprocess.assert_called_once()


def test_admin_status_success(client):
    """GET /api/admin/status returns status active."""
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "admin panel active"
    assert "warning" in data
