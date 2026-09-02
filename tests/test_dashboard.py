def test_dashboard_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
