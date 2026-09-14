def test_list_accounts_returns_200(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_get_account_by_id_returns_404_when_not_found(client):
    # Empty DB, account not found
    res = client.get("/api/accounts/999")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data
