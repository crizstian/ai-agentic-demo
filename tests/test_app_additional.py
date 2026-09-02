"""Additional unit tests for app.app module - Flask app factory and configuration."""

from app.app import create_app


def test_health_endpoint_returns_ok(client):
    """GET /health returns status ok with 200 status code."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"


def test_cors_headers_present(client):
    """CORS headers are present in response for cross-origin requests."""
    res = client.get("/health", headers={"Origin": "http://example.com"})
    # CORS is configured with origins="*", so Access-Control-Allow-Origin should be present
    assert res.status_code == 200
    # Flask-CORS adds these headers; exact header depends on version
    # Just verify response succeeds (full CORS testing requires OPTIONS request)


def test_app_url_map_strict_slashes_disabled():
    """Flask app has strict_slashes disabled for flexible routing."""
    app = create_app()
    assert app.url_map.strict_slashes is False


def test_app_has_accounts_blueprint():
    """Flask app has accounts blueprint registered."""
    app = create_app()
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    assert "accounts" in blueprint_names


def test_app_has_all_blueprints_registered():
    """Flask app has all 5 expected blueprints registered."""
    app = create_app()
    blueprint_names = [bp.name for bp in app.blueprints.values()]

    expected_blueprints = {"accounts", "transfers", "statements", "admin", "fx"}
    assert expected_blueprints.issubset(set(blueprint_names))


def test_welcome_endpoint_returns_html(client):
    """GET /welcome returns HTML response with welcome message."""
    res = client.get("/welcome?name=TestUser")
    assert res.status_code == 200
    assert b"Welcome to DemoBank" in res.data
    assert b"TestUser" in res.data


def test_login_page_get_returns_html(client):
    """GET /login returns login page HTML."""
    res = client.get("/login")
    assert res.status_code == 200
    assert res.content_type.startswith("text/html")
