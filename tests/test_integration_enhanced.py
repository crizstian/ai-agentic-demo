"""Enhanced integration tests - end-to-end happy path scenarios."""


def test_complete_transfer_flow(client):
    """End-to-end: create accounts, perform transfer, verify transaction record."""
    from app.db import get_db

    db = get_db()

    # Create source and destination accounts
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-src", "Source User", 1000.00, "checking"]
    )
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-dest", "Dest User", 500.00, "savings"]
    )
    db.commit()

    # Perform transfer
    payload = {
        "fromAccount": "acc-src",
        "toAccount": "acc-dest",
        "amount": 250.00,
        "memo": "Integration test transfer"
    }
    transfer_res = client.post("/api/transfers", json=payload)
    assert transfer_res.status_code == 200

    # Verify transaction was recorded
    transfers = client.get("/api/transfers").get_json()
    assert len(transfers) == 1
    assert transfers[0]["amount"] == 250.00
    assert transfers[0]["memo"] == "Integration test transfer"


def test_dashboard_displays_recent_activity(client):
    """End-to-end: seed data, verify dashboard shows accounts and transactions."""
    from app.db import get_db

    db = get_db()

    # Seed accounts
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-001", "Alice", 2000.00, "checking"]
    )

    # Seed transactions
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo) VALUES (?, ?, ?, ?)",
        ["acc-001", "acc-002", 100.00, "Recent activity"]
    )
    db.commit()

    # Load dashboard
    res = client.get("/")
    assert res.status_code == 200
    assert b"Alice" in res.data
    assert b"Recent activity" in res.data
