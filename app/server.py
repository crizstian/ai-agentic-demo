from .app import create_app
from .config import config
from .db import get_db, init_db

init_db()

_db = get_db()
if _db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
    from scripts.seed import seed
    seed()

app = create_app()


def main():
    print(f"DemoBank AI SDLC running on http://localhost:{config['port']}")
    print("WARNING: This app is intentionally vulnerable. DEMO USE ONLY.")
    app.run(host="0.0.0.0", port=config["port"])


if __name__ == "__main__":
    main()
