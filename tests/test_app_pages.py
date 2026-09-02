"""Enhanced unit tests for app.py page routes - happy path scenarios only."""


def test_dashboard_with_accounts(client):
    """GET / renders dashboard with accounts list."""
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-dash-001", "Dashboard User", 5000.00, "checking"]
    )
    db.commit()

    res = client.get("/")
    assert res.status_code == 200
    assert b"Dashboard User" in res.data


def test_dashboard_with_transactions(client):
    """Dashboard displays recent transactions."""
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        ["acc-001", "acc-002", 150.00, "Test transaction", "completed"]
    )
    db.commit()

    res = client.get("/")
    assert res.status_code == 200
    assert b"Test transaction" in res.data


def test_dashboard_empty_state(client):
    """Dashboard renders successfully with no accounts or transactions."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"DemoBank AI SDLC" in res.data


def test_transfer_page_with_accounts(client):
    """GET /transfer renders transfer form with account options."""
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["acc-transfer-001", "Transfer Test", 1000.00, "checking"]
    )
    db.commit()

    res = client.get("/transfer")
    assert res.status_code == 200
    assert b"Transfer Test" in res.data


def test_transfer_page_empty_accounts(client):
    """Transfer page renders with no accounts available."""
    res = client.get("/transfer")
    assert res.status_code == 200
    assert b"DemoBank AI SDLC" in res.data


def test_pay_bill_page_renders(client):
    """GET /pay-bill renders bill payment page."""
    res = client.get("/pay-bill")
    assert res.status_code == 200
    assert b"DemoBank AI SDLC" in res.data


def test_login_page_get(client):
    """GET /login renders login form."""
    res = client.get("/login")
    assert res.status_code == 200
    assert b"DemoBank AI SDLC" in res.data


def test_login_submit_redirects(client):
    """POST /login accepts any credentials and redirects to dashboard."""
    res = client.post("/login", data={"username": "test", "password": "test"})
    assert res.status_code == 302
    assert res.location == "/"


def test_welcome_page_with_name(client):
    """GET /welcome?name=<name> displays personalized greeting."""
    res = client.get("/welcome?name=Alice")
    assert res.status_code == 200
    assert b"Welcome to DemoBank, Alice!" in res.data


def test_welcome_page_default_guest(client):
    """GET /welcome without name param defaults to Guest."""
    res = client.get("/welcome")
    assert res.status_code == 200
    assert b"Welcome to DemoBank, Guest!" in res.data
