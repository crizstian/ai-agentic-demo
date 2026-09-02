import os

JWT_SECRET = os.environ.get("JWT_SECRET", "")
API_KEY = os.environ.get("API_KEY", "")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

config = {
    "port": int(os.environ.get("PORT", 3000)),
    "db_path": os.environ.get("DB_PATH", "./demobank.db"),
    "jwt_secret": JWT_SECRET,
    "api_key": API_KEY,
    "access_token": ACCESS_TOKEN,
    "app_name": "DemoBank AI SDLC",
    "demo_mode": True,
}
