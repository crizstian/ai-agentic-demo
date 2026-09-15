def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_pay_bill_page_returns_200(client):
    res = client.get("/pay-bill")
    assert res.status_code == 200


def test_login_page_get_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_login_post_redirects_to_dashboard(client):
    res = client.post("/login", data={"username": "test", "password": "test"})
    assert res.status_code == 302
    assert res.location == "/"
