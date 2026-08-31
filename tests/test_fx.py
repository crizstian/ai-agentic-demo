def test_fx_rates_returns_200(client):
    res = client.get("/api/fx")
    assert res.status_code == 200


def test_fx_rates_has_usd_base(client):
    data = client.get("/api/fx").get_json()
    assert data["base"] == "USD"


def test_fx_rates_contains_all_currencies(client):
    rates = client.get("/api/fx").get_json()["rates"]
    for currency in ("USD", "EUR", "GBP", "JPY", "CAD"):
        assert currency in rates


def test_fx_rates_usd_is_one(client):
    rates = client.get("/api/fx").get_json()["rates"]
    assert rates["USD"] == 1.0
