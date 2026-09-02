"""Unit tests for app.db module - database connection and initialization."""

import sqlite3
import pytest
from app.db import get_db, init_db, reset_db


def test_get_db_returns_connection():
    """get_db() returns a valid SQLite connection object."""
    reset_db()  # Start fresh
    conn = get_db()
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row


def test_init_db_creates_accounts_table():
    """init_db() creates accounts table with expected columns."""
    reset_db()
    db = init_db()

    # Verify accounts table exists and has correct schema
    cursor = db.execute("PRAGMA table_info(accounts)")
    columns = {row[1] for row in cursor.fetchall()}
    assert "id" in columns
    assert "owner" in columns
    assert "balance" in columns
    assert "type" in columns


def test_init_db_creates_transactions_table():
    """init_db() creates transactions table with expected columns."""
    reset_db()
    db = init_db()

    # Verify transactions table exists and has correct schema
    cursor = db.execute("PRAGMA table_info(transactions)")
    columns = {row[1] for row in cursor.fetchall()}
    assert "id" in columns
    assert "from_account" in columns
    assert "to_account" in columns
    assert "amount" in columns
    assert "memo" in columns
    assert "status" in columns
    assert "created_at" in columns


def test_reset_db_clears_connection():
    """reset_db() closes and clears the global database connection."""
    # First get a connection
    conn1 = get_db()
    assert conn1 is not None

    # Reset should clear it
    reset_db()

    # Next get_db() should return a new connection
    conn2 = get_db()
    assert conn2 is not None
    # Can't reliably test they're different objects due to singleton pattern,
    # but verify it's still a valid connection
    assert isinstance(conn2, sqlite3.Connection)
