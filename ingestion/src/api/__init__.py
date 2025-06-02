"""
Career-Hi API package
"""

from .models import RetrievalRequest, RetrievalResponse, CourseInfo
from fastapi import APIRouter
from .routes import router as retrieval_router

# 메인 라우터 생성
router = APIRouter(prefix="/api/v1")

# 서브 라우터들 등록
router.include_router(retrieval_router, tags=["retrieval"])

__all__ = ["RetrievalRequest", "RetrievalResponse", "CourseInfo", "router"]
