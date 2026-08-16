import os
import warnings

JWT_SECRET = os.environ.get("JWT_SECRET")
API_KEY = os.environ.get("API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

if not JWT_SECRET or not API_KEY or not ACCESS_TOKEN:
    warnings.warn(
        "One or more required secrets (JWT_SECRET, API_KEY, ACCESS_TOKEN) are not set. "
        "This application must not be deployed to production without these values.",
        RuntimeWarning,
        stacklevel=2,
    )

config = {
    "port": int(os.environ.get("PORT", 3000)),
    "db_path": os.environ.get("DB_PATH", "./demobank.db"),
    "jwt_secret": JWT_SECRET,
    "api_key": API_KEY,
    "access_token": ACCESS_TOKEN,
    "app_name": "DemoBank AI SDLC",
    "demo_mode": True,
}
