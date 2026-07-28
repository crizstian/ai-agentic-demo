import os

# FIXED: Hardcoded secrets vulnerability - secrets must be provided via environment variables
# No fallback values to prevent accidental use of weak defaults in production
JWT_SECRET = os.environ.get("JWT_SECRET")
API_KEY = os.environ.get("API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Validate that secrets are provided in production environments
if not JWT_SECRET and os.environ.get("ENV", "development") == "production":
    raise ValueError("JWT_SECRET environment variable must be set in production")
if not API_KEY and os.environ.get("ENV", "development") == "production":
    raise ValueError("API_KEY environment variable must be set in production")
if not ACCESS_TOKEN and os.environ.get("ENV", "development") == "production":
    raise ValueError("ACCESS_TOKEN environment variable must be set in production")

config = {
    "port": int(os.environ.get("PORT", 3000)),
    "db_path": os.environ.get("DB_PATH", "./demobank.db"),
    "jwt_secret": JWT_SECRET,
    "api_key": API_KEY,
    "access_token": ACCESS_TOKEN,
    "app_name": "DemoBank AI SDLC",
    "demo_mode": True,
}
