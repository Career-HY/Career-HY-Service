from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from util.logging import setup_logging

# 로깅 설정 초기화
setup_logging()

app = FastAPI(
    title="Career-Hi Ingestion API",
    description="Document retrieval and processing API for Career-Hi",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 구체적인 origin으로 변경해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Career-Hi Ingestion API! 6/8 07:20 test",
    }
