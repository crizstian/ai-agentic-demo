import pytest
from app.db import get_db


def _seed_account(db, id="acc1", owner="Alice", balance=1000.0, type="checking"):
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        (id, owner, balance, type),
    )
    db.commit()


def test_list_accounts_empty(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_accounts_returns_seeded_rows(client):
    db = get_db()
    _seed_account(db, id="acc1", owner="Alice", balance=500.0)
    _seed_account(db, id="acc2", owner="Bob", balance=250.0)

    res = client.get("/api/accounts/")
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2
    owners = {row["owner"] for row in data}
    assert owners == {"Alice", "Bob"}


def test_get_account_returns_account(client):
    db = get_db()
    _seed_account(db, id="acc99", owner="Carol", balance=1234.56)

    res = client.get("/api/accounts/acc99")
    assert res.status_code == 200
    body = res.get_json()
    assert body["id"] == "acc99"
    assert body["owner"] == "Carol"
    assert body["balance"] == pytest.approx(1234.56)


def test_get_account_not_found_returns_404(client):
    res = client.get("/api/accounts/does-not-exist")
    assert res.status_code == 404
    assert "error" in res.get_json()
