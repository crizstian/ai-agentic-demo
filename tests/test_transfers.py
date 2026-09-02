def test_create_transfer_success(client):
    """POST /api/transfers with valid fields returns success and transferId."""
    payload = {
        "fromAccount": "acc-001",
        "toAccount": "acc-002",
        "amount": 100.50,
        "memo": "Test payment"
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "transferId" in data
    assert data["amount"] == 100.50


def test_create_transfer_with_memo(client):
    """POST /api/transfers with memo returns transfer with correct memo."""
    payload = {
        "fromAccount": "acc-003",
        "toAccount": "acc-004",
        "amount": 250.00,
        "memo": "Rent payment"
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["message"] == "Transfer completed successfully"


def test_list_transfers_empty(client):
    """GET /api/transfers returns empty list when no transfers exist."""
    res = client.get("/api/transfers")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_transfers_returns_recent(client):
    """GET /api/transfers returns recently created transfers."""
    # Create a transfer first
    payload = {
        "fromAccount": "acc-005",
        "toAccount": "acc-006",
        "amount": 75.25,
        "memo": "Utility bill"
    }
    client.post("/api/transfers", json=payload)

    res = client.get("/api/transfers")
    assert res.status_code == 200
    transfers = res.get_json()
    assert len(transfers) == 1
    assert transfers[0]["amount"] == 75.25
    assert transfers[0]["memo"] == "Utility bill"
