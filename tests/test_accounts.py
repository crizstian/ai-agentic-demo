"""Unit tests for the accounts API endpoints."""


def test_list_accounts_returns_200(client):
    response = client.get("/api/accounts/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_account_not_found_returns_404(client):
    response = client.get("/api/accounts/99999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_admin_status_returns_200(client):
    response = client.get("/api/admin/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "admin panel active"
