import os

config = {
    "port": int(os.environ.get("PORT", 3000)),
    "db_path": os.environ.get("DB_PATH", "./demobank.db"),
    "jwt_secret": os.environ.get("JWT_SECRET"),
    "api_key": os.environ.get("API_KEY"),
    "access_token": os.environ.get("ACCESS_TOKEN"),
    "app_name": "DemoBank AI SDLC",
    "demo_mode": True,
}
