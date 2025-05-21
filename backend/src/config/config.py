import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parents[1] / ".env"
load_dotenv(env_path)

class Settings:
    APP_NAME: str = "Career-Hi Backend"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    # DB_URL, SECRET_KEY 등 나중에 추가
    # DB_URL: str = os.getenv("DB_URL")

settings = Settings()
