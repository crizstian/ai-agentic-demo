from app.db import get_db, init_db, reset_db


def test_init_db_creates_accounts_table():
    reset_db()
    init_db()
    tables = [
        r[0]
        for r in get_db()
        .execute("SELECT name FROM sqlite_master WHERE type='table'")
        .fetchall()
    ]
    assert "accounts" in tables


def test_init_db_creates_transactions_table():
    reset_db()
    init_db()
    tables = [
        r[0]
        for r in get_db()
        .execute("SELECT name FROM sqlite_master WHERE type='table'")
        .fetchall()
    ]
    assert "transactions" in tables


def test_get_db_returns_same_connection():
    reset_db()
    init_db()
    conn1 = get_db()
    conn2 = get_db()
    assert conn1 is conn2
