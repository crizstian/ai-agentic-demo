"""Additional happy-path unit tests to reach the 10-test minimum."""


def test_welcome_page_returns_200(client):
    res = client.get("/welcome?name=Alice")
    assert res.status_code == 200
    assert b"Alice" in res.data


def test_login_get_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_pay_bill_page_returns_200(client):
    res = client.get("/pay-bill")
    assert res.status_code == 200
