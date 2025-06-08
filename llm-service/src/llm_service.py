from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.config.config import settings
from src.utils.logging import setup_logging

# 로깅 설정 초기화
setup_logging()

app = FastAPI(
    title="Career-Hi LLM Service",
    description="Career-Hi LLM Service API",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Career-Hi LLM Service 6/8 09:20 test",
        "status": "running",
        "version": "1.0.0",
        "model": settings.OPENAI_MODEL,
    }
