from fastapi import APIRouter, HTTPException
from typing import Dict
from src.api.models import LLMRequest, LLMResponse
from src.services.llm_prompting import LLMPromptingService
from src.config.config import settings
from src.services.ingestion_client import IngestionClient

router = APIRouter(
    prefix="/api/v1",
    tags=["LLM Service"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/generatellm",
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
    try:
        # Ingestion 서비스에서 관련 문서 검색
        ingestion_client = IngestionClient()
        # 서비스 상태 확인
        if not await ingestion_client.health_check():
            raise HTTPException(
                status_code=503, detail="Ingestion service is not available"
            )
        relevant_docs = await ingestion_client.retrieve_documents(
            request.profile, limit=10
        )

        # LLM 서비스로 응답 생성
        llm_service = LLMPromptingService()
        response = await llm_service.generate_response(
            query=request.query, documents=relevant_docs
        )

        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/health",
#     summary="서비스 상태 확인",
#     description="LLM 서비스의 현재 상태와 설정을 확인합니다.",
#     response_description="서비스 상태 정보",
#     responses={
#         200: {
#             "description": "서비스가 정상적으로 동작 중",
#             "content": {
#                 "application/json": {
#                     "example": {"status": "healthy", "version": "1.0", "model": "gpt-4"}
#                 }
#             },
#         }
#     },
# )
# async def health_check():
#     """서비스 상태를 확인합니다."""
#     return {"status": "healthy", "version": "1.0", "model": settings.OPENAI_MODEL}
