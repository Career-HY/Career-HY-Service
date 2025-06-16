from fastapi import APIRouter, HTTPException
from typing import Dict
from src.api.models import LLMRequest, LLMResponse
from src.services.llm_prompting import LLMPromptingService
from src.config.config import settings
from src.services.ingestion_client import IngestionClient

router = APIRouter()
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
    try:
        # 프로필에 query 설정 (Pydantic copy 메서드 사용)
        profile_with_query = request.profile.copy(update={'query': request.query})

        # Ingestion 서비스에서 관련 문서 검색
        ingestion_client = IngestionClient()
        relevant_docs = await ingestion_client.retrieve_documents(
            profile_with_query
        )

        # LLM 서비스로 응답 생성
        llm_service = LLMPromptingService()
        response = await llm_service.generate_response(
            query=request.query, 
            documents=relevant_docs,
            profile=profile_with_query,
            chat_history=request.chat_history
        )
 
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

