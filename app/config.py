import os

JWT_SECRET = os.environ.get("JWT_SECRET")
API_KEY = os.environ.get("API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Fail fast if any required secret is absent in production.
# Uses an explicit opt-out (ALLOW_MISSING_SECRETS=true) so that production
# instances that omit ENV are not silently bypassed — the inverse of the
# prior pattern which defaulted to "development" and skipped validation.
_is_dev = os.environ.get("ALLOW_MISSING_SECRETS", "").lower() == "true"
if not _is_dev:
    for _name, _val in (("JWT_SECRET", JWT_SECRET), ("API_KEY", API_KEY), ("ACCESS_TOKEN", ACCESS_TOKEN)):
        if not _val:
            raise ValueError(
                f"{_name} environment variable must be set. "
                "Set ALLOW_MISSING_SECRETS=true to bypass in local development."
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
