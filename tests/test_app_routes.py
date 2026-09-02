from app.db import get_db


def test_dashboard_loads_successfully(client):
    """GET / returns 200 status code."""
    res = client.get("/")
    assert res.status_code == 200


def test_dashboard_renders_accounts(client):
    """Dashboard HTML contains accounts from database."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["dash-001", "Dashboard User", 5000.00, "checking"]
    )
    db.commit()

    res = client.get("/")
    assert res.status_code == 200
    assert b"Dashboard User" in res.data


def test_dashboard_renders_transactions(client):
    """Dashboard HTML contains recent transactions."""
    db = get_db()
    db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        ["acc-001", "acc-002", 150.00, "Dashboard test", "completed"]
    )
    db.commit()

    res = client.get("/")
    assert res.status_code == 200
    assert b"150" in res.data or b"150.0" in res.data


def test_transfer_page_loads(client):
    """GET /transfer returns 200 status code."""
    res = client.get("/transfer")
    assert res.status_code == 200


def test_transfer_page_renders_accounts(client):
    """Transfer page contains accounts from database."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["transfer-001", "Transfer User", 1000.00, "savings"]
    )
    db.commit()

    res = client.get("/transfer")
    assert res.status_code == 200
    assert b"Transfer User" in res.data


def test_pay_bill_page_loads(client):
    """GET /pay-bill returns 200 status code."""
    res = client.get("/pay-bill")
    assert res.status_code == 200


def test_login_page_get(client):
    """GET /login returns 200 status code."""
    res = client.get("/login")
    assert res.status_code == 200


def test_login_page_renders_form(client):
    """Login page contains login form elements."""
    res = client.get("/login")
    assert res.status_code == 200
    assert b"login" in res.data.lower()


def test_login_post_redirects(client):
    """POST /login redirects to dashboard."""
    res = client.post("/login", data={"username": "test", "password": "test"})
    assert res.status_code == 302
    assert res.location == "/" or res.location.endswith("/")


def test_welcome_default_name(client):
    """GET /welcome without name parameter uses 'Guest'."""
    res = client.get("/welcome")
    assert res.status_code == 200
    assert b"Guest" in res.data


def test_welcome_with_name(client):
    """GET /welcome?name=Alice returns welcome message with name."""
    res = client.get("/welcome?name=Alice")
    assert res.status_code == 200
    assert b"Alice" in res.data


def test_dashboard_empty_state(client):
    """Dashboard with empty database returns 200."""
    res = client.get("/")
    assert res.status_code == 200


def test_transfer_page_empty_state(client):
    """Transfer page with empty database returns 200."""
    res = client.get("/transfer")
    assert res.status_code == 200


def test_strict_slashes_disabled(client):
    """Both /api/fx and /api/fx/ return same response."""
    res1 = client.get("/api/fx")
    res2 = client.get("/api/fx/")
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.get_json() == res2.get_json()
