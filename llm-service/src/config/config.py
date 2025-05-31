import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Career-Hi LLM Service"
    DEBUG: bool = True
    
    # OpenAI API 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 5003
    
    # Career-Hi Backend API 엔드포인트
    BACKEND_API_URL: str = "http://backend:5001"
    
    # 기타 설정
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 