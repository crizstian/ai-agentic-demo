def test_dashboard_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200


def test_transfer_page_returns_200(client):
    res = client.get("/transfer")
    assert res.status_code == 200


def test_dashboard_pay_bill_action_links_to_bill_payment_page(client):
    res = client.get("/")
    text = res.get_data(as_text=True)
    assert 'href="/pay-bill"' in text
    assert "Pay Bill" in text


def test_pay_bill_returns_200(client):
    res = client.get("/pay-bill")
    assert res.status_code == 200
    assert "Pay Bill" in res.get_data(as_text=True)


def test_login_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_quick_action_cards_are_not_rotated(client):
    """Regression for HD-200712: quick-action/transaction button cards must not
    carry the rotate()/translateY() transforms that made them overlap and appear
    misaligned on the dashboard."""
    res = client.get("/styles.css")
    assert res.status_code == 200
    css = res.get_data(as_text=True)
    assert "rotate(" not in css
    assert ".action-card:nth-child" not in css
