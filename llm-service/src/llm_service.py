from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config.config import settings

app = FastAPI(
    title=settings.APP_NAME, 
    debug=settings.DEBUG,
    description="Career-Hi LLM Service API",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi LLM Service!!"}

