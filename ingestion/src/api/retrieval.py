from fastapi import APIRouter, HTTPException
from .models import RetrievalRequest, RetrievalResponse
from src.embedder import OpenAITextEmbedder
from src.vector import query_chroma
from backend.src.util.logging import log_api_call

# 라우터 설정
router = APIRouter()


@router.post("/retrieval", response_model=RetrievalResponse)
@log_api_call
async def retrieve_documents(request: RetrievalRequest) -> RetrievalResponse:
    """
    문서 검색 API 엔드포인트

    Parameters:
    - request: RetrievalRequest - 검색 요청 데이터
        - query: 검색 쿼리
        - major: 전공
        - catalogs: 강의 목록
        - interest_job: 관심 직무 목록
        - certification: 자격증 목록

    Returns:
    - RetrievalResponse - 검색된 문서 목록
    """
    try:
        # TODO: 실제 검색 로직 구현
        # 1. 쿼리 처리와 전공 기반 필터링
        # 2. 강의 목록에서 관련 문서 검색
        # 3. 관심 직무와 자격증 정보 활용

        # 임시 응답 (실제 구현 전)
        retrieved_docs = [
            f"Query '{request.query}' related document",
            f"Major: {request.major} specific content",
            f"Found relevant content from {len(request.catalogs)} courses",
            f"Job interests: {', '.join(request.interest_job)}",
            f"Certifications: {', '.join(request.certification)}",
        ]

        return RetrievalResponse(docs=retrieved_docs)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during document retrieval"
        )
