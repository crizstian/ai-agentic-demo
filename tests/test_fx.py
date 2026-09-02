def test_fx_returns_exchange_rates(client):
    """Test GET /api/fx/ returns exchange rates"""
    res = client.get("/api/fx/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] == "demo"
    assert data["base"] == "USD"
    assert "rates" in data
    assert "USD" in data["rates"]
