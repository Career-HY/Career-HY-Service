import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """LLM 서비스 설정"""

    # 애플리케이션 설정
    APP_NAME: str = "Career-Hi LLM Service"
    DEBUG: bool = True

    # OpenAI API 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Ingestion API 설정
    INGESTION_SERVICE_URL: str
    INGESTION_REQUEST_TIMEOUT: float = 30.0  # 초
    MAX_DOCUMENTS: int = 10  # 검색할 최대 문서 수

    # LLM 설정
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Langsmith 설정
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "career-hi-rag"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
