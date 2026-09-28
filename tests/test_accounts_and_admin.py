"""Happy-path unit tests for accounts and admin routes."""

import json


def test_list_accounts_returns_200(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_get_account_not_found_returns_404(client):
    res = client.get("/api/accounts/nonexistent-id")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data


def test_admin_status_returns_active(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "admin panel active"


def test_admin_ping_returns_result(client):
    res = client.get("/api/admin/ping?host=localhost")
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data


def test_login_post_redirects(client):
    res = client.post("/login", data={"username": "user", "password": "pass"})
    assert res.status_code in (301, 302, 308)
