def test_statements_list_returns_200(client):
    res = client.get("/api/statements")
    assert res.status_code == 200


def test_statements_list_has_entries(client):
    data = client.get("/api/statements").get_json()
    assert len(data["statements"]) == 3


def test_statements_download_missing_file(client):
    res = client.get("/api/statements?file=nonexistent.pdf")
    assert res.status_code == 404


def test_statements_path_traversal_blocked(client):
    res = client.get("/api/statements?file=../../etc/passwd")
    assert res.status_code == 400
