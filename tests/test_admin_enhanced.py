"""Enhanced unit tests for admin routes - happy path scenarios only."""


def test_admin_ping_with_valid_hostname(client):
    """GET /api/admin/ping?host=<valid> returns success with hostname."""
    res = client.get("/api/admin/ping?host=example.com")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "example.com"
    assert "Pinging: example.com" in data["result"]


def test_admin_ping_default_localhost(client):
    """GET /api/admin/ping without host param defaults to localhost."""
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "localhost"
    assert "Pinging: localhost" in data["result"]


def test_admin_ping_with_hyphenated_hostname(client):
    """Ping accepts hostnames with hyphens (valid DNS format)."""
    res = client.get("/api/admin/ping?host=my-server.local")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "my-server.local"


def test_admin_ping_with_subdomain(client):
    """Ping accepts multi-level subdomains."""
    res = client.get("/api/admin/ping?host=api.prod.example.com")
    assert res.status_code == 200
    data = res.get_json()
    assert data["host"] == "api.prod.example.com"


def test_admin_status_returns_active(client):
    """GET /api/admin/status returns active status with demo warning."""
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "admin panel active"
    assert "DEMO ONLY" in data["warning"]
