from fastapi import FastAPI
from api.retrieval import router as retrieval_router

app = FastAPI(
    title="Career-Hi Ingestion Service",
    description="S3 데이터 로드 및 벡터 검색 서비스",
    version="1.0.0"
)

# API 라우터 등록
app.include_router(retrieval_router, prefix="/api/v1", tags=["retrieval"])

@app.get("/")
async def root():
    return {"message": "Career-Hi Ingestion Service is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 