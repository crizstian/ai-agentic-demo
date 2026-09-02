def test_get_account_by_id_success(client):
    """GET /api/accounts/<id> returns existing account."""
    # First insert a test account
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-test-001", "Alice Smith", 1500.00, "checking"]
    )
    db.commit()

    res = client.get("/api/accounts/acc-test-001")
    assert res.status_code == 200
    account = res.get_json()
    assert account["id"] == "acc-test-001"
    assert account["owner"] == "Alice Smith"
    assert account["balance"] == 1500.00


def test_list_accounts_success(client):
    """GET /api/accounts/ returns all accounts."""
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-test-002", "Bob Jones", 2500.00, "savings"]
    )
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-test-003", "Carol White", 3000.00, "checking"]
    )
    db.commit()

    res = client.get("/api/accounts/")
    assert res.status_code == 200
    accounts = res.get_json()
    assert len(accounts) == 2
    assert accounts[0]["id"] == "acc-test-002"
    assert accounts[1]["id"] == "acc-test-003"


def test_list_accounts_empty(client):
    """GET /api/accounts/ returns empty list when no accounts exist."""
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []
