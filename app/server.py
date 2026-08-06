from .app import create_app
from .config import config
from .db import init_db

init_db()
app = create_app()


def main():
    bind_host = "0.0.0.0" if config.get("container_mode") else "127.0.0.1"
    print(f"DemoBank AI SDLC running on http://localhost:{config['port']}")
    print("WARNING: This app is intentionally vulnerable. DEMO USE ONLY.")
    app.run(host=bind_host, port=config["port"], debug=False)


if __name__ == "__main__":
    main()
