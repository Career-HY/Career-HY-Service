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
    
    # 세션 설정
    SESSION_COOKIE_DOMAIN: str = None if DEBUG else os.getenv("SESSION_COOKIE_DOMAIN")  # 개발환경에서는 None, 운영환경에서는 환경변수 값 사용
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "none")
    
    # LLM Service 설정
    LLM_SERVICE_URL: str = os.getenv("LLM_SERVICE_URL")
    LLM_REQUEST_TIMEOUT: float = 30.0

settings = Settings()
