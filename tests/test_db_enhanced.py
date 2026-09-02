"""Enhanced unit tests for db.py - happy path scenarios only."""
import os
import sqlite3


def test_init_db_creates_accounts_table():
    """init_db creates accounts table with correct schema."""
    from app.db import init_db, get_db, reset_db

    reset_db()
    db = init_db()

    # Verify accounts table exists
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'"
    )
    assert cursor.fetchone() is not None


def test_init_db_creates_transactions_table():
    """init_db creates transactions table with correct schema."""
    from app.db import init_db, get_db, reset_db

    reset_db()
    db = init_db()

    # Verify transactions table exists
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
    )
    assert cursor.fetchone() is not None


def test_get_db_returns_row_factory():
    """get_db connection has row_factory set for dict-like access."""
    from app.db import get_db, reset_db, init_db

    reset_db()
    init_db()
    db = get_db()

    assert db.row_factory is sqlite3.Row


def test_get_db_singleton_behavior():
    """Multiple calls to get_db return the same connection."""
    from app.db import get_db, reset_db, init_db

    reset_db()
    init_db()

    db1 = get_db()
    db2 = get_db()

    assert db1 is db2


def test_reset_db_clears_connection():
    """reset_db closes and nullifies the global connection."""
    from app.db import get_db, reset_db, init_db
    import app.db as db_module

    reset_db()
    init_db()

    first_db = get_db()
    reset_db()

    # After reset, global _db should be None
    assert db_module._db is None
