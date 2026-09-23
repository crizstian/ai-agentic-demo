import os
from unittest.mock import MagicMock, patch

# Use an in-memory DB for the whole test session, mirroring the Node tests'
# process.env.DB_PATH = ":memory:". Set before any app import so config picks it up.
os.environ["DB_PATH"] = ":memory:"

# Mock split.io before any app imports to avoid blocking during test init
mock_split_client = MagicMock()
mock_split_client.get_treatment.return_value = "on"
mock_split_factory = MagicMock()
mock_split_factory.client.return_value = mock_split_client
mock_split_factory.block_until_ready = MagicMock()

with patch("splitio.get_factory", return_value=mock_split_factory):
    import pytest

    from app.app import create_app
    from app.db import init_db, reset_db


@pytest.fixture()
def client():
    """Fresh in-memory DB + Flask test client per test.

    Blueprints hold a reference to app.db.get_db, whose `_db` global we rebuild
    here via reset_db()/init_db() — same module object, so no reload is needed.
    """
    reset_db()
    init_db()

    # Seed test data
    from app.db import get_db
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["1", "Test User", 1000.0, "checking"],
    )
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) VALUES (?, ?, ?, ?)",
        ["2", "Test User 2", 2000.0, "savings"],
    )
    db.commit()

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c
