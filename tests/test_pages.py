def test_transfer_page_returns_200(client):
    """Test GET /transfer returns transfer page"""
    res = client.get("/transfer")
    assert res.status_code == 200


def test_pay_bill_page_returns_200(client):
    """Test GET /pay-bill returns bill payment page"""
    res = client.get("/pay-bill")
    assert res.status_code == 200


def test_login_page_returns_200(client):
    """Test GET /login returns login page"""
    res = client.get("/login")
    assert res.status_code == 200
