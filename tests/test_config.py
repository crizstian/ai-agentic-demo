"""Unit tests for app.config module - configuration management."""

import os
from app.config import config


def test_config_has_required_keys():
    """config dictionary contains all required configuration keys."""
    required_keys = {
        "port",
        "db_path",
        "jwt_secret",
        "api_key",
        "access_token",
        "app_name",
        "demo_mode"
    }
    assert required_keys.issubset(config.keys())


def test_config_port_has_default_value():
    """config['port'] defaults to 3000 when PORT env var is not set."""
    # Note: This test assumes PORT is not set in test environment
    # The config module reads os.environ.get("PORT", 3000)
    if "PORT" not in os.environ:
        assert config["port"] == 3000
    else:
        # If PORT is set, verify it's an integer
        assert isinstance(config["port"], int)


def test_config_app_name_is_demobank():
    """config['app_name'] is set to 'DemoBank AI SDLC'."""
    assert config["app_name"] == "DemoBank AI SDLC"


def test_config_demo_mode_is_true():
    """config['demo_mode'] is True for demo environment."""
    assert config["demo_mode"] is True
