import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as main_router
from src.api.routes_gt import router as gt_router
from src.config.config import settings
from src.utils.logging import setup_logging
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

# LangSmith 환경 변수 설정 (자동 트레이싱용)
os.environ["LANGSMITH_TRACING"] = str(settings.LANGSMITH_TRACING).lower()
os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT

# 로깅 설정 초기화
setup_logging()

logger = logging.getLogger(__name__)

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
app.include_router(main_router)
app.include_router(gt_router)


@app.get("/")
def root():
    return {
        "service": "Career-Hi LLM Service 6/8 10:50 test",
        "status": "running",
        "version": "1.0.0",
        "model": settings.OPENAI_MODEL,
    }

# ------------------------------------------------------------------
# 🔧 Request Validation Error 로깅
# ------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 검증 오류를 상세히 로깅한 뒤 기본 422 응답."""
    try:
        body = await request.body()
        logger.error(
            "❌ RequestValidationError | path=%s | errors=%s | body=%s",
            request.url.path,
            exc.errors(),
            body.decode("utf-8", errors="ignore")[:1000],  # 과도한 길이 제한
        )
    except Exception:
        logger.exception("검증 오류 로깅 중 추가 예외 발생")

    return JSONResponse(status_code=422, content={"detail": exc.errors()})
