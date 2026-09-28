import os

# Use an in-memory DB for the whole test session, mirroring the Node tests'
# process.env.DB_PATH = ":memory:". Set before any app import so config picks it up.
os.environ["DB_PATH"] = ":memory:"

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
