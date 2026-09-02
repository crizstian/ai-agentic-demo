"""Enhanced unit tests for statements route - happy path scenarios only."""
import os
from unittest.mock import patch, MagicMock


def test_statements_list_without_file_param(client):
    """GET /api/statements without file param returns list of available statements."""
    res = client.get("/api/statements/")
    assert res.status_code == 200
    data = res.get_json()
    assert "statements" in data
    assert len(data["statements"]) == 3
    assert data["statements"][0]["name"] == "statement-jan-2024.pdf"


def test_statements_list_structure(client):
    """GET /api/statements returns statements with name and date fields."""
    res = client.get("/api/statements/")
    assert res.status_code == 200
    data = res.get_json()
    for stmt in data["statements"]:
        assert "name" in stmt
        assert "date" in stmt


def test_statements_list_dates_formatted(client):
    """Statement dates are in YYYY-MM-DD format."""
    res = client.get("/api/statements/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["statements"][0]["date"] == "2024-01-31"
    assert data["statements"][1]["date"] == "2024-02-29"
    assert data["statements"][2]["date"] == "2024-03-31"


@patch("app.routes.statements.send_file")
@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.os.path.realpath")
def test_statements_download_valid_file(mock_realpath, mock_exists, mock_send_file, client):
    """GET /api/statements?file=<valid> returns file with proper path resolution."""
    base_dir = "/fake/demo-statements"
    file_path = f"{base_dir}/statement-jan-2024.pdf"

    mock_realpath.side_effect = [base_dir, file_path]
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock(status_code=200)

    res = client.get("/api/statements/?file=statement-jan-2024.pdf")
    assert mock_send_file.called
    assert mock_send_file.call_args[1]["as_attachment"] is True


@patch("app.routes.statements.send_file")
@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.os.path.realpath")
def test_statements_download_feb_statement(mock_realpath, mock_exists, mock_send_file, client):
    """Download February statement succeeds with valid filename."""
    base_dir = "/fake/demo-statements"
    file_path = f"{base_dir}/statement-feb-2024.pdf"

    mock_realpath.side_effect = [base_dir, file_path]
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock(status_code=200)

    res = client.get("/api/statements/?file=statement-feb-2024.pdf")
    assert mock_send_file.called


@patch("app.routes.statements.send_file")
@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.os.path.realpath")
def test_statements_download_mar_statement(mock_realpath, mock_exists, mock_send_file, client):
    """Download March statement succeeds with valid filename."""
    base_dir = "/fake/demo-statements"
    file_path = f"{base_dir}/statement-mar-2024.pdf"

    mock_realpath.side_effect = [base_dir, file_path]
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock(status_code=200)

    res = client.get("/api/statements/?file=statement-mar-2024.pdf")
    assert mock_send_file.called


@patch("app.routes.statements.send_file")
@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.os.path.realpath")
def test_statements_path_resolution_logic(mock_realpath, mock_exists, mock_send_file, client):
    """Valid file request triggers realpath resolution for security check."""
    base_dir = "/fake/demo-statements"
    file_path = f"{base_dir}/statement-jan-2024.pdf"

    mock_realpath.side_effect = [base_dir, file_path]
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock(status_code=200)

    client.get("/api/statements/?file=statement-jan-2024.pdf")
    assert mock_realpath.call_count == 2  # Called for base and file_path


@patch("app.routes.statements.send_file")
@patch("app.routes.statements.os.path.exists")
@patch("app.routes.statements.os.path.realpath")
def test_statements_send_file_as_attachment(mock_realpath, mock_exists, mock_send_file, client):
    """send_file is called with as_attachment=True for downloads."""
    base_dir = "/fake/demo-statements"
    file_path = f"{base_dir}/statement-jan-2024.pdf"

    mock_realpath.side_effect = [base_dir, file_path]
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock(status_code=200)

    client.get("/api/statements/?file=statement-jan-2024.pdf")
    call_kwargs = mock_send_file.call_args[1]
    assert call_kwargs["as_attachment"] is True
