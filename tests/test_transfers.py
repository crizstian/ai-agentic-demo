def test_list_transfers_returns_200(client):
    res = client.get("/api/transfers/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_create_transfer_with_valid_data_returns_success(client):
    payload = {
        "fromAccount": "1",
        "toAccount": "2",
        "amount": 100.00,
        "memo": "Test transfer"
    }
    res = client.post("/api/transfers/", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "transferId" in data
