import os
from unittest.mock import patch


def test_statements_list_success(client):
    """GET /api/statements without file returns list of available statements."""
    res = client.get("/api/statements")
    assert res.status_code == 200
    data = res.get_json()
    assert "statements" in data
    statements = data["statements"]
    assert len(statements) == 3
    assert statements[0]["name"] == "statement-jan-2024.pdf"
    assert statements[1]["name"] == "statement-feb-2024.pdf"
    assert statements[2]["name"] == "statement-mar-2024.pdf"


@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.send_file")
def test_statements_download_valid_file(mock_send_file, mock_exists, client):
    """GET /api/statements?file=<valid> returns file (mocked)."""
    mock_exists.return_value = True
    mock_send_file.return_value = "mocked-file-response"

    res = client.get("/api/statements?file=statement-jan-2024.pdf")
    # send_file returns a response object; we just verify it was called
    mock_send_file.assert_called_once()
    assert mock_exists.called


def test_statements_blocks_path_traversal(client):
    """GET /api/statements with path traversal returns 400."""
    res = client.get("/api/statements?file=../../../etc/passwd")
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid file path"
