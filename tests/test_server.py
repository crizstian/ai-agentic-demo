"""Unit tests for app.server module - application entry point."""

from unittest.mock import patch, MagicMock
from app.server import app


def test_app_is_flask_instance():
    """server.app is a Flask application instance."""
    from flask import Flask
    assert isinstance(app, Flask)


def test_app_has_test_client_method():
    """server.app provides test_client() method for testing."""
    assert hasattr(app, 'test_client')
    assert callable(app.test_client)


@patch('app.server.app.run')
def test_main_calls_app_run(mock_run):
    """main() function calls app.run() with correct parameters."""
    from app.server import main

    main()

    # Verify app.run was called once
    mock_run.assert_called_once()
    # Verify it was called with host and port
    call_kwargs = mock_run.call_args[1]
    assert call_kwargs['host'] == '0.0.0.0'
    assert 'port' in call_kwargs
