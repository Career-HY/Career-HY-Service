from fastapi import APIRouter, HTTPException
from typing import Dict
from src.api.models import LLMRequest, LLMResponse
from src.services.llm_prompting import LLMPromptingService
from src.config.config import settings
from src.services.ingestion_client import IngestionClient
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post(
    "/generate-llm",
    response_model=LLMResponse,
    summary="LLM 응답 생성",
    description="""
    사용자의 질문과 프로필을 기반으로 맞춤형 LLM 응답을 생성합니다.
    
    - 관련 문서를 검색하여 컨텍스트로 활용
    - GPT 모델을 사용하여 응답 생성
    - 에러 발생 시 적절한 에러 메시지 반환
    """,
    response_description="생성된 LLM 응답",
    responses={
        200: {
            "description": "성공적으로 응답 생성",
            "content": {
                "application/json": {
                    "example": {
                        "response": "귀하의 프로필을 분석한 결과, 다음과 같은 조언을 드립니다...",
                        "metadata": {
                            "model": "gpt-4",
                            "tokens_used": 150,
                            "processing_time": "2.5s",
                        },
                    }
                }
            },
        },
        503: {
            "description": "Ingestion 서비스 사용 불가",
            "content": {
                "application/json": {
                    "example": {"detail": "Ingestion service is not available"}
                }
            },
        },
    },
)
async def generate_llm_response(request: LLMRequest):
    """LLM 응답을 생성합니다."""
    # -----------------------------
    # 요청 수신 로깅
    # -----------------------------
    try:
        logger.info(
            "📥 /generate-llm 요청 수신 | query_len=%s | chat_history_len=%s",
            len(request.query),
            len(request.chat_history or []),
        )
        logger.debug("요청 본문: %s", request.model_dump())
    except Exception:
        # 로깅 중 오류가 나더라도 요청 처리는 계속
        logger.warning("요청 로깅 중 오류가 발생했습니다.")

    try:
        # 프로필에 query 설정 (Pydantic copy 메서드 사용)
        profile_with_query = request.profile.copy(update={'query': request.query})

        # LLM 서비스 초기화
        llm_service = LLMPromptingService()

        # --------------------------------------------------
        # 1) 의도 분류 선행 → 검색 필요 여부 판단
        # --------------------------------------------------
        intent = await llm_service.classify_query_intent(
            request.query,
            request.chat_history,
        )

        # --------------------------------------------------
        # 2) 의도에 따라 문서 검색 여부 결정
        # --------------------------------------------------
        if intent == "SEARCH_NEEDED":
            ingestion_client = IngestionClient()
            relevant_docs = await ingestion_client.retrieve_documents(profile_with_query)
        else:
            relevant_docs = []

        # --------------------------------------------------
        # 3) 최종 응답 생성 (의도 전달)
        # --------------------------------------------------
        response = await llm_service.generate_response(
            query=request.query,
            documents=relevant_docs,
            profile=profile_with_query,
            chat_history=request.chat_history,
            intent=intent,
        )

        logger.info("✅ LLM 응답 생성 완료 | recommended_jobs=%s", len(response.recommended_jobs))
        return response
    
    except Exception as e:
        logger.error("💥 LLM 응답 생성 실패: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

