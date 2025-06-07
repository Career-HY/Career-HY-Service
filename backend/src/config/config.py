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
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
    # CORS 설정 - 쉼표로 구분된 도메인 목록
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS")
    
    # LLM Service 설정
    LLM_SERVICE_URL: str = os.getenv("LLM_SERVICE_URL")
    LLM_REQUEST_TIMEOUT: float = 30.0

settings = Settings()
