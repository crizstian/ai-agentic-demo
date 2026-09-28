def test_login_page_get(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_login_submit_redirects(client):
    res = client.post("/login", data={"username": "demo", "password": "demo"})
    assert res.status_code in (301, 302, 308)


def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_pay_bill_page_returns_200(client):
    res = client.get("/pay-bill")
    assert res.status_code == 200


def test_welcome_page_returns_200(client):
    res = client.get("/welcome?name=Tester")
    assert res.status_code == 200
    assert b"Tester" in res.data
