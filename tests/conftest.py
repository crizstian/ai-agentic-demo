import os
import sys
from unittest.mock import MagicMock

# Use an in-memory DB for the whole test session, mirroring the Node tests'
# process.env.DB_PATH = ":memory:". Set before any app import so config picks it up.
os.environ["DB_PATH"] = ":memory:"
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake")

# Mock splitio before app import — the SDK blocks on network at module level.
_factory_mock = MagicMock()
_splitio_mock = MagicMock()
_splitio_mock.get_factory.return_value = _factory_mock
sys.modules.setdefault("splitio", _splitio_mock)

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

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c
