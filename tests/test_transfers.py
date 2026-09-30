def test_create_transfer_success(client):
    res = client.post(
        "/api/transfers/",
        json={"fromAccount": "acc-A", "toAccount": "acc-B", "amount": 50.0, "memo": "lunch"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "transferId" in data
    assert data["amount"] == 50.0


def test_create_transfer_missing_fields(client):
    res = client.post("/api/transfers/", json={"fromAccount": "acc-A"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_list_transfers_returns_list(client):
    res = client.get("/api/transfers/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
