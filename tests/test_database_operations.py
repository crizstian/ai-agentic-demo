"""Unit tests for database operations and data persistence.

These tests verify happy path database CRUD operations work correctly.
"""

from app.db import get_db, init_db, reset_db


def test_insert_and_retrieve_account():
    """Insert account into database and retrieve it successfully."""
    reset_db()
    db = init_db()

    # Insert account
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["test-acc-001", "Test Owner", 1234.56, "checking"]
    )
    db.commit()

    # Retrieve account
    row = db.execute("SELECT * FROM accounts WHERE id = ?", ["test-acc-001"]).fetchone()

    assert row is not None
    assert row["id"] == "test-acc-001"
    assert row["owner"] == "Test Owner"
    assert row["balance"] == 1234.56


def test_insert_and_retrieve_transaction():
    """Insert transaction into database and retrieve it successfully."""
    reset_db()
    db = init_db()

    # Insert transaction
    cursor = db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        ["acc-001", "acc-002", 500.00, "Test transaction", "completed"]
    )
    db.commit()
    transaction_id = cursor.lastrowid

    # Retrieve transaction
    row = db.execute("SELECT * FROM transactions WHERE id = ?", [transaction_id]).fetchone()

    assert row is not None
    assert row["from_account"] == "acc-001"
    assert row["to_account"] == "acc-002"
    assert row["amount"] == 500.00
    assert row["memo"] == "Test transaction"


def test_database_commit_persists_data():
    """Database commit persists inserted data across queries."""
    reset_db()
    db = init_db()

    # Insert and commit
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["persist-001", "Persist User", 9999.99, "savings"]
    )
    db.commit()

    # Query in new cursor
    row = db.execute("SELECT * FROM accounts WHERE id = ?", ["persist-001"]).fetchone()

    assert row is not None
    assert row["balance"] == 9999.99


def test_row_factory_returns_dict_like_rows():
    """SQLite row factory allows dict-like access to row fields."""
    reset_db()
    db = init_db()

    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["row-factory-001", "Factory User", 555.55, "checking"]
    )
    db.commit()

    row = db.execute("SELECT * FROM accounts WHERE id = ?", ["row-factory-001"]).fetchone()

    # Dict-like access
    assert row["id"] == "row-factory-001"
    assert row["owner"] == "Factory User"
    assert dict(row)["balance"] == 555.55


def test_multiple_account_inserts_all_persist():
    """Multiple account inserts all persist in database."""
    reset_db()
    db = init_db()

    accounts = [
        ("multi-001", "User A", 100.00, "checking"),
        ("multi-002", "User B", 200.00, "savings"),
        ("multi-003", "User C", 300.00, "checking"),
    ]

    for acc_id, owner, balance, acc_type in accounts:
        db.execute(
            "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
            [acc_id, owner, balance, acc_type]
        )
    db.commit()

    # Count rows
    count = db.execute("SELECT COUNT(*) as cnt FROM accounts").fetchone()["cnt"]

    assert count == 3


def test_transaction_status_defaults_to_completed():
    """Transaction status defaults to 'completed' when not specified."""
    reset_db()
    db = init_db()

    # Insert without explicit status
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo) VALUES (?, ?, ?, ?)",
        ["acc-a", "acc-b", 75.00, "Default status test"]
    )
    db.commit()

    row = db.execute("SELECT status FROM transactions WHERE memo = ?", ["Default status test"]).fetchone()

    assert row["status"] == "completed"


def test_query_transactions_by_account():
    """Query transactions filtered by account ID returns matching records."""
    reset_db()
    db = init_db()

    # Insert transactions
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        ["query-acc-001", "other-acc", 100.00, "From query account", "completed"]
    )
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        ["other-acc", "query-acc-001", 50.00, "To query account", "completed"]
    )
    db.commit()

    # Query by from_account
    rows = db.execute(
        "SELECT * FROM transactions WHERE from_account = ?",
        ["query-acc-001"]
    ).fetchall()

    assert len(rows) == 1
    assert rows[0]["memo"] == "From query account"


def test_account_balance_stored_as_real():
    """Account balance is stored as REAL (float) type in database."""
    reset_db()
    db = init_db()

    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["balance-001", "Balance User", 1234.567, "checking"]
    )
    db.commit()

    row = db.execute("SELECT balance FROM accounts WHERE id = ?", ["balance-001"]).fetchone()

    assert isinstance(row["balance"], float)
    assert row["balance"] == 1234.567
