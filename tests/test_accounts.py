def test_list_accounts_empty(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_accounts_with_data(client):
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES ('acc1', 'Alice', 1000.0, 'checking')"
    )
    db.commit()

    res = client.get("/api/accounts/")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["owner"] == "Alice"
    assert data[0]["balance"] == 1000.0


def test_get_account_not_found(client):
    res = client.get("/api/accounts/nonexistent")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_get_account_found(client):
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES ('acc2', 'Bob', 500.0, 'savings')"
    )
    db.commit()

    res = client.get("/api/accounts/acc2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == "acc2"
    assert data["owner"] == "Bob"
    assert data["type"] == "savings"
