"""Integration tests for multi-step workflows and API composition.

These tests verify happy path scenarios where multiple components work together.
"""

from app.db import get_db


def test_complete_transfer_workflow(client):
    """Complete transfer flow: create accounts, execute transfer, verify transaction."""
    db = get_db()

    # Arrange: Create source and destination accounts
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-src-001", "Source User", 1000.00, "checking"]
    )
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-dst-001", "Dest User", 500.00, "savings"]
    )
    db.commit()

    # Act: Execute transfer
    payload = {
        "fromAccount": "acc-src-001",
        "toAccount": "acc-dst-001",
        "amount": 250.00,
        "memo": "Integration test transfer"
    }
    res = client.post("/api/transfers", json=payload)

    # Assert: Transfer succeeded
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["amount"] == 250.00


def test_dashboard_displays_multiple_accounts(client):
    """Dashboard aggregates and displays multiple accounts from database."""
    db = get_db()

    # Arrange: Create multiple accounts
    accounts_data = [
        ("acc-dash-001", "User One", 1500.00, "checking"),
        ("acc-dash-002", "User Two", 2500.00, "savings"),
        ("acc-dash-003", "User Three", 750.00, "checking"),
    ]
    for acc_id, owner, balance, acc_type in accounts_data:
        db.execute(
            "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
            [acc_id, owner, balance, acc_type]
        )
    db.commit()

    # Act: Load dashboard
    res = client.get("/")

    # Assert: All accounts appear
    assert res.status_code == 200
    assert b"User One" in res.data
    assert b"User Two" in res.data
    assert b"User Three" in res.data


def test_transfer_appears_in_transaction_list(client):
    """Created transfer appears in GET /api/transfers list."""
    # Arrange & Act: Create transfer
    payload = {
        "fromAccount": "acc-100",
        "toAccount": "acc-200",
        "amount": 99.99,
        "memo": "Test transaction list"
    }
    post_res = client.post("/api/transfers", json=payload)
    transfer_id = post_res.get_json()["transferId"]

    # Act: Retrieve transfers list
    get_res = client.get("/api/transfers")

    # Assert: Transfer is in list
    assert get_res.status_code == 200
    transfers = get_res.get_json()
    assert len(transfers) >= 1
    assert any(t["id"] == transfer_id for t in transfers)


def test_accounts_api_returns_json_array(client):
    """GET /api/accounts returns valid JSON array structure."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-json-001", "JSON Test", 1000.00, "checking"]
    )
    db.commit()

    res = client.get("/api/accounts/")

    assert res.status_code == 200
    assert res.content_type == "application/json"
    accounts = res.get_json()
    assert isinstance(accounts, list)
    assert len(accounts) == 1


def test_fx_api_accessible_via_blueprint(client):
    """FX API is accessible through blueprint URL prefix /api/fx."""
    res = client.get("/api/fx")

    assert res.status_code == 200
    data = res.get_json()
    assert "rates" in data
    assert "USD" in data["rates"]


def test_admin_status_endpoint_returns_json(client):
    """Admin status endpoint returns JSON with expected structure."""
    res = client.get("/api/admin/status")

    assert res.status_code == 200
    assert res.content_type == "application/json"
    data = res.get_json()
    assert "status" in data


def test_statements_list_returns_multiple_items(client):
    """Statements API returns list of multiple statement entries."""
    res = client.get("/api/statements")

    assert res.status_code == 200
    data = res.get_json()
    assert "statements" in data
    assert len(data["statements"]) >= 3


def test_transfer_with_zero_memo_succeeds(client):
    """Transfer with empty memo string completes successfully."""
    payload = {
        "fromAccount": "acc-memo-001",
        "toAccount": "acc-memo-002",
        "amount": 50.00,
        "memo": ""
    }
    res = client.post("/api/transfers", json=payload)

    assert res.status_code == 200
    assert res.get_json()["success"] is True


def test_account_detail_returns_complete_fields(client):
    """GET /api/accounts/<id> returns all expected account fields."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-detail-001", "Detail User", 3500.50, "savings"]
    )
    db.commit()

    res = client.get("/api/accounts/acc-detail-001")

    assert res.status_code == 200
    account = res.get_json()
    assert account["id"] == "acc-detail-001"
    assert account["owner"] == "Detail User"
    assert account["balance"] == 3500.50
    assert account["type"] == "savings"


def test_multiple_transfers_all_succeed(client):
    """Multiple sequential transfers all complete successfully."""
    transfers = [
        {"fromAccount": "a1", "toAccount": "a2", "amount": 10.00, "memo": "First"},
        {"fromAccount": "a2", "toAccount": "a3", "amount": 20.00, "memo": "Second"},
        {"fromAccount": "a3", "toAccount": "a1", "amount": 30.00, "memo": "Third"},
    ]

    for transfer in transfers:
        res = client.post("/api/transfers", json=transfer)
        assert res.status_code == 200
        assert res.get_json()["success"] is True
