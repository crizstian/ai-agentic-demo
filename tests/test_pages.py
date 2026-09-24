def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_login_get_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_login_post_redirects_to_dashboard(client):
    res = client.post("/login", data={"username": "demo", "password": "demo"})
    assert res.status_code in (301, 302, 308)
    assert res.headers["Location"].endswith("/")


def test_welcome_returns_html(client):
    res = client.get("/welcome?name=TestUser")
    assert res.status_code == 200
    assert b"DemoBank" in res.data
