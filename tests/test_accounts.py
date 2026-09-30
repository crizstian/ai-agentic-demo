from app.db import get_db


def test_list_accounts_returns_empty_list(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_accounts_with_seeded_data(client):
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-001", "Alice", 1000.0, "checking"],
    )
    db.commit()

    res = client.get("/api/accounts/")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == "acc-001"
    assert data[0]["owner"] == "Alice"


def test_get_account_not_found(client):
    res = client.get("/api/accounts/nonexistent")
    assert res.status_code == 404
    assert "error" in res.get_json()
