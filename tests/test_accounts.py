def test_get_account_returns_account_data(client):
    """Test GET /api/accounts/<id> returns account details"""
    from app.db import get_db

    # Create a sample account
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ("1", "John Doe", 1000.0, "checking")
    )
    db.commit()

    res = client.get("/api/accounts/1")
    assert res.status_code == 200
    data = res.get_json()
    assert "id" in data
    assert "balance" in data


def test_list_accounts_returns_all_accounts(client):
    """Test GET /api/accounts/ returns list of accounts"""
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
