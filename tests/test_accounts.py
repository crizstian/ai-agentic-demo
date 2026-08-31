from app.db import get_db


def _seed_accounts():
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) "
        "VALUES (1, 'Alice Johnson', 50000.0, 'checking')"
    )
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) "
        "VALUES (2, 'Bob Smith', 25000.0, 'savings')"
    )
    db.commit()


def test_get_accounts_returns_list(client):
    _seed_accounts()
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) == 2


def test_get_accounts_with_search(client):
    _seed_accounts()
    res = client.get("/api/accounts/1")
    assert res.status_code == 200
    body = res.get_json()
    assert body["owner"] == "Alice Johnson"
    assert body["balance"] == 50000.0


def test_sql_injection_in_search(client):
    """Verify the SQL injection vulnerability works with ' OR 1=1--."""
    _seed_accounts()
    res = client.get("/api/accounts/%27%20OR%201%3D1--")
    assert res.status_code == 200
    body = res.get_json()
    assert "owner" in body


def test_get_account_details_by_id(client):
    _seed_accounts()
    res = client.get("/api/accounts/1/details")
    assert res.status_code == 200
    body = res.get_json()
    assert body["owner"] == "Alice Johnson"
    assert body["balance"] == 50000.0
    assert "recent_transactions" in body


def test_get_account_details_nonexistent_404(client):
    res = client.get("/api/accounts/999/details")
    assert res.status_code == 404
    body = res.get_json()
    assert "error" in body


def test_bola_idor_no_auth_check(client):
    """Both accounts accessible without any auth -- BOLA/IDOR vuln."""
    _seed_accounts()
    res1 = client.get("/api/accounts/1/details")
    res2 = client.get("/api/accounts/2/details")
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.get_json()["owner"] == "Alice Johnson"
    assert res2.get_json()["owner"] == "Bob Smith"


def test_accounts_returns_empty_when_no_data(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []
