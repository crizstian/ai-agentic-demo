def test_list_accounts_returns_200(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_get_account_by_id_returns_200(client):
    res = client.get("/api/accounts/1")
    assert res.status_code == 200
    data = res.get_json()
    assert "id" in data


def test_create_transfer_returns_200(client):
    res = client.post(
        "/api/transfers/",
        json={
            "fromAccount": "1",
            "toAccount": "2",
            "amount": 100.0,
            "memo": "Test transfer",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True


def test_list_transfers_returns_200(client):
    res = client.get("/api/transfers/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_list_statements_returns_200(client):
    res = client.get("/api/statements/")
    assert res.status_code == 200
    data = res.get_json()
    assert "statements" in data


def test_fx_rates_returns_200(client):
    res = client.get("/api/fx/")
    assert res.status_code == 200
    data = res.get_json()
    assert "rates" in data
    assert data["base"] == "USD"


def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_login_page_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200
