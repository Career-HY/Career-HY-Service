import httpx
import logging
from typing import Dict, Any, List, Optional
from config.config import settings
from schemas.chat import LLMServiceRequest, LLMServiceResponse
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class LLMServiceClient:
    """LLM 서비스와 통신하는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.LLM_SERVICE_URL
        self.timeout = settings.LLM_REQUEST_TIMEOUT
    
    async def generate_response(
        self, 
        query: str, 
        profile: Dict,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> LLMServiceResponse:
        """
        LLM 서비스에 요청을 보내 응답을 생성합니다.
        
        Args:
            query: 사용자 질문
            profile: 사용자 프로필
            chat_history: 대화 이력 (선택적)
            
        Returns:
            LLMServiceResponse: LLM 응답과 추천 채용공고
        """
        try:
            # 대화 이력 로깅
            if chat_history:
                logger.info(f"📝 전달되는 대화 이력 (최근 {len(chat_history)}개):")
                for msg in chat_history:
                    logger.info(f"  - {msg['role']}: {msg['content'][:50]}...")
            else:
                logger.info("❌ 전달되는 대화 이력 없음")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate-llm",
                    json={
                        "query": query,
                        "profile": profile,
                        "chat_history": chat_history
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=503,
                        detail="LLM 서비스 응답 오류"
                    )
                
                response_data = response.json()
                return LLMServiceResponse(
                    content=response_data["content"],
                    recommended_jobs=response_data["recommended_jobs"]
                )
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="LLM 서비스에 연결할 수 없습니다."
            )
            
    async def generate_response_old(self, query: str, profile: Dict[str, Any]) -> LLMServiceResponse:
        """
        LLM 서비스에 요청을 보내고 응답을 받습니다.
        
        Args:
            query: 사용자 질문
            profile: 사용자 프로필 정보
            
        Returns:
            LLMServiceResponse: LLM 서비스 응답
            
        Raises:
            Exception: LLM 서비스 호출 실패 시
        """
        request_data = LLMServiceRequest(query=query, profile=profile)
        url = f"{self.base_url}/generate-llm"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"LLM 서비스 요청: {url}")
                logger.debug(f"요청 데이터: {request_data.model_dump()}")
                
                response = await client.post(
                    url,
                    json=request_data.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                response_data = response.json()
                logger.info("LLM 서비스 응답 수신 완료")
                logger.debug(f"응답 데이터: {response_data}")
                
                return LLMServiceResponse(**response_data)
            
        except Exception as e:
            logger.error(f"LLM 서비스 호출 중 예상치 못한 오류: {str(e)}")
            raise Exception("LLM 서비스 호출 중 오류가 발생했습니다. 관리자에게 문의해주세요.") 