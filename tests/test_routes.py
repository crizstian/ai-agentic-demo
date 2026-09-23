def test_list_accounts_returns_200(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_get_account_returns_200(client):
    # Create an account first
    from app.db import get_db
    db = get_db()
    db.execute("INSERT INTO accounts (id, owner, balance, type) VALUES ('1', 'Test User', 1000.0, 'checking')")
    db.commit()

    res = client.get("/api/accounts/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == "1"


def test_fx_rates_returns_200_and_rates(client):
    res = client.get("/api/fx/")
    assert res.status_code == 200
    data = res.get_json()
    assert "rates" in data
    assert data["base"] == "USD"


def test_create_transfer_returns_200(client):
    payload = {
        "fromAccount": "1",
        "toAccount": "2",
        "amount": 100.0,
        "memo": "Test transfer"
    }
    res = client.post("/api/transfers/", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True


def test_list_transfers_returns_200(client):
    res = client.get("/api/transfers/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_admin_status_returns_200(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data


def test_admin_ping_returns_200(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data


def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200
