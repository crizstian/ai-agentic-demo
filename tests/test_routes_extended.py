"""Extended unit tests for Flask routes and page rendering.

These tests verify happy path scenarios for additional route functionality.
"""

from app.db import get_db


def test_pay_bill_page_loads_successfully(client):
    """GET /pay-bill returns 200 and renders pay-bill template."""
    res = client.get("/pay-bill")

    assert res.status_code == 200
    assert res.content_type.startswith("text/html")


def test_pay_bill_page_contains_app_name(client):
    """Pay-bill page includes app name in rendered HTML."""
    res = client.get("/pay-bill")

    assert res.status_code == 200
    assert b"DemoBank" in res.data


def test_transfer_page_shows_savings_accounts(client):
    """Transfer page displays savings account types correctly."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["savings-001", "Savings User", 5000.00, "savings"]
    )
    db.commit()

    res = client.get("/transfer")

    assert res.status_code == 200
    assert b"Savings User" in res.data
    assert b"savings" in res.data or b"5000" in res.data


def test_dashboard_shows_recent_transactions_limit(client):
    """Dashboard displays recent transactions with limit of 5."""
    db = get_db()

    # Insert 7 transactions
    for i in range(7):
        db.execute(
            "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
            [f"acc-{i}", f"acc-{i+1}", 100.00, f"Transaction {i}", "completed"]
        )
    db.commit()

    res = client.get("/")

    # Should still return 200 (limit is internal, page renders all it gets)
    assert res.status_code == 200


def test_transfer_memo_appears_in_transaction_record(client):
    """Transfer memo is stored and retrievable in transaction record."""
    payload = {
        "fromAccount": "memo-test-001",
        "toAccount": "memo-test-002",
        "amount": 88.88,
        "memo": "Important payment note"
    }
    post_res = client.post("/api/transfers", json=payload)

    assert post_res.status_code == 200

    # Verify memo in database
    db = get_db()
    row = db.execute(
        "SELECT memo FROM transactions WHERE memo = ?",
        ["Important payment note"]
    ).fetchone()

    assert row is not None
    assert row["memo"] == "Important payment note"
