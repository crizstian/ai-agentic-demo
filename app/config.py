import os
import sys

JWT_SECRET = os.environ.get("JWT_SECRET", "")
API_KEY = os.environ.get("API_KEY", "")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

if not JWT_SECRET or not API_KEY or not ACCESS_TOKEN:
    print(
        "WARNING: JWT_SECRET, API_KEY, and ACCESS_TOKEN must be set via environment "
        "variables or a secrets manager. Running without them is insecure.",
        file=sys.stderr,
    )

config = {
    "port": int(os.environ.get("PORT", 3000)),
    "db_path": os.environ.get("DB_PATH", "./demobank.db"),
    "jwt_secret": JWT_SECRET,
    "api_key": API_KEY,
    "access_token": ACCESS_TOKEN,
    "app_name": "DemoBank AI SDLC",
    "demo_mode": True,
    "container_mode": os.environ.get("CONTAINER_MODE", "false").lower() == "true",
}
