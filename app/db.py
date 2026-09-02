import sqlite3

from .config import config

_db = None


def get_db():
    """Return a shared sqlite3 connection, mirroring the Node getDb() singleton."""
    global _db
    if _db is None:
        # check_same_thread=False so the single connection can serve Flask's
        # request threads, matching the Node app's one shared handle.
        _db = sqlite3.connect(config["db_path"], check_same_thread=False)
        _db.row_factory = sqlite3.Row
    return _db


def init_db():
    database = get_db()
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
          id TEXT PRIMARY KEY,
          owner TEXT NOT NULL,
          balance REAL NOT NULL DEFAULT 0,
          type TEXT NOT NULL DEFAULT 'checking'
        )
        """
    )
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          from_account TEXT,
          to_account TEXT,
          amount REAL NOT NULL,
          memo TEXT,
          status TEXT DEFAULT 'completed',
          created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    database.commit()
    return database


def reset_db():
    """Drop the cached connection (used by tests to rebuild a fresh in-memory DB)."""
    global _db
    if _db is not None:
        _db.close()
    _db = None
