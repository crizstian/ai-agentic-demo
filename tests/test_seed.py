from app.db import get_db, init_db, reset_db
from scripts.seed import seed


def test_seed_creates_five_accounts():
    reset_db()
    init_db()
    seed()
    rows = get_db().execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    assert rows == 5


def test_seed_creates_transactions():
    reset_db()
    init_db()
    seed()
    rows = get_db().execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert rows == 8


def test_seed_is_idempotent():
    reset_db()
    init_db()
    seed()
    seed()
    rows = get_db().execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    assert rows == 5


def test_seed_account_names_match():
    reset_db()
    init_db()
    seed()
    names = [
        r[0] for r in get_db().execute("SELECT owner FROM accounts ORDER BY id").fetchall()
    ]
    assert names == [
        "Alice Johnson",
        "Bob Smith",
        "Charlie Brown",
        "Diana Martinez",
        "Edward Kim",
    ]
