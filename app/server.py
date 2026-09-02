from .app import create_app
from .config import config
from .db import init_db

init_db()
app = create_app()


def main():
    print(f"DemoBank AI SDLC running on http://localhost:{config['port']}")
    print("WARNING: This app is intentionally vulnerable. DEMO USE ONLY.")
    app.run(host="0.0.0.0", port=config["port"])


if __name__ == "__main__":
    main()
