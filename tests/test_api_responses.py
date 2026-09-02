"""Unit tests for API response formats and consistency.

These tests verify happy path API responses follow expected patterns.
"""

from app.db import get_db


def test_fx_api_response_has_required_fields(client):
    """FX API response contains all required fields in expected structure."""
    res = client.get("/api/fx")

    assert res.status_code == 200
    data = res.get_json()

    # Verify all required fields present
    assert "source" in data
    assert "base" in data
    assert "rates" in data
    assert "updated" in data
    assert "disclaimer" in data


def test_transfer_success_response_structure(client):
    """Successful transfer returns response with expected JSON structure."""
    payload = {
        "fromAccount": "resp-001",
        "toAccount": "resp-002",
        "amount": 123.45,
        "memo": "Response test"
    }
    res = client.post("/api/transfers", json=payload)

    assert res.status_code == 200
    data = res.get_json()

    # Verify response structure
    assert "success" in data
    assert "message" in data
    assert "transferId" in data
    assert "amount" in data
    assert data["success"] is True


def test_account_api_response_content_type(client):
    """Account API responses have correct JSON content-type header."""
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["ct-001", "Content Type Test", 500.00, "checking"]
    )
    db.commit()

    res = client.get("/api/accounts/ct-001")

    assert res.status_code == 200
    assert res.content_type == "application/json"


def test_health_endpoint_json_structure(client):
    """Health endpoint returns simple JSON with status field."""
    res = client.get("/health")

    assert res.status_code == 200
    data = res.get_json()

    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"


def test_statements_api_returns_json_object(client):
    """Statements API returns JSON object (not array) with statements field."""
    res = client.get("/api/statements")

    assert res.status_code == 200
    data = res.get_json()

    assert isinstance(data, dict)
    assert "statements" in data
    assert isinstance(data["statements"], list)


def test_admin_ping_response_includes_host(client):
    """Admin ping response includes host field matching request parameter."""
    res = client.get("/api/admin/ping?host=testhost")

    assert res.status_code == 200
    data = res.get_json()

    assert "host" in data
    assert "result" in data
    assert data["host"] == "testhost"


def test_transfer_list_returns_array_of_objects(client):
    """GET /api/transfers returns JSON array of transaction objects."""
    # Create a transfer first
    payload = {
        "fromAccount": "arr-001",
        "toAccount": "arr-002",
        "amount": 50.00,
        "memo": "Array test"
    }
    client.post("/api/transfers", json=payload)

    res = client.get("/api/transfers")

    assert res.status_code == 200
    data = res.get_json()

    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
