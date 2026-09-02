def test_fx_returns_rates(client):
    """GET /api/fx returns structure with expected currency rates."""
    res = client.get("/api/fx")
    assert res.status_code == 200
    data = res.get_json()
    assert "rates" in data
    rates = data["rates"]
    assert rates["USD"] == 1.0
    assert rates["EUR"] == 0.92
    assert rates["GBP"] == 0.79
    assert rates["JPY"] == 149.5
    assert rates["CAD"] == 1.36


def test_fx_response_structure(client):
    """GET /api/fx response contains all required fields."""
    res = client.get("/api/fx")
    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] == "demo"
    assert data["base"] == "USD"
    assert "rates" in data
    assert data["updated"] == "2024-01-15T12:00:00Z"
    assert "disclaimer" in data
