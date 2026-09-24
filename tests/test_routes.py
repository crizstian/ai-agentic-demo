"""Happy-path unit tests for accounts, admin, and page routes."""
import os

os.environ.setdefault("DB_PATH", ":memory:")

import pytest

from app.app import create_app
from app.db import init_db, reset_db


@pytest.fixture()
def client():
    reset_db()
    init_db()
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def seeded_client(client):
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ("acc-001", "Alice", 500.0, "checking"),
    )
    db.commit()
    return client


# --- Accounts ---

def test_list_accounts_empty(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_accounts_returns_seeded_account(seeded_client):
    res = seeded_client.get("/api/accounts/")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["owner"] == "Alice"


def test_get_account_found(seeded_client):
    res = seeded_client.get("/api/accounts/acc-001")
    assert res.status_code == 200
    body = res.get_json()
    assert body["id"] == "acc-001"
    assert body["balance"] == 500.0


def test_get_account_not_found(client):
    res = client.get("/api/accounts/nonexistent")
    assert res.status_code == 404
    assert "error" in res.get_json()


# --- Admin ---

def test_admin_status(client):
    res = client.get("/api/admin/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "admin panel active"


def test_admin_ping_default_host(client):
    res = client.get("/api/admin/ping")
    assert res.status_code == 200
    body = res.get_json()
    assert "result" in body
    assert body["host"] == "localhost"


# --- Page routes ---

def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_pay_bill_page_returns_200(client):
    res = client.get("/pay-bill")
    assert res.status_code == 200


def test_login_page_get_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_login_post_redirects(client):
    res = client.post("/login", data={"username": "demo", "password": "demo"})
    assert res.status_code in (301, 302, 308)
