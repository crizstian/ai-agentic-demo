from app.config import config


def test_config_has_port():
    assert "port" in config


def test_config_port_is_integer():
    assert isinstance(config["port"], int)


def test_config_has_db_path():
    assert "db_path" in config
