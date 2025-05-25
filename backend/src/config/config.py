import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parents[1] / ".env"
load_dotenv(env_path)

class Settings:
    APP_NAME: str = "Career-Hi Backend"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "replace-with-your-secret")
    

settings = Settings()
