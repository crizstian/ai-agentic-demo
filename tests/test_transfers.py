def test_create_transfer_with_valid_data(client):
    """Test POST /api/transfers/ creates a transfer"""
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
    assert data["amount"] == 100.00


def test_list_transfers_returns_transactions(client):
    """Test GET /api/transfers/ returns list of transactions"""
    res = client.get("/api/transfers/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
