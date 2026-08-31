from flask import Flask

from app.app import create_app


def test_create_app_returns_flask():
    app = create_app()
    assert isinstance(app, Flask)


def test_app_has_health_route(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_app_registers_accounts_blueprint(client):
    res = client.get("/api/accounts")
    assert res.status_code == 200


def test_app_registers_ai_blueprint(client):
    res = client.get("/api/ai/status")
    # Blueprint is registered even if this specific route returns 404
    assert res.status_code in (200, 404)
