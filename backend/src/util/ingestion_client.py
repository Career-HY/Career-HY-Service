import httpx
import logging
from typing import Dict, Any, Optional
from config.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class IngestionClient:
    """Ingestion 서비스와 통신하는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.INGESTION_SERVICE_URL
        self.timeout = 10.0
    
    async def get_posting(self, rec_idx: str) -> Optional[Dict[str, Any]]:
        """
        Ingestion 서비스에서 채용공고 메타데이터를 조회합니다.
        
        Args:
            rec_idx: 채용공고 ID
            
        Returns:
            Dict[str, Any]: 채용공고 메타데이터와 요약 (rec_idx, metadata, excerpt)
            None: 조회 실패 시
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Ingestion 서비스 요청: {self.base_url}/post/{rec_idx}")
                
                response = await client.get(f"{self.base_url}/post/{rec_idx}")
                response.raise_for_status()
                
                response_data = response.json()
                logger.debug(f"채용공고 {rec_idx} 메타데이터 조회 완료")
                
                return response_data
                
        except httpx.RequestError as e:
            logger.error(f"Ingestion 서비스 연결 실패 (rec_idx: {rec_idx}): {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"채용공고 {rec_idx}를 찾을 수 없습니다")
            else:
                logger.error(f"Ingestion 서비스 응답 오류 (rec_idx: {rec_idx}): {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"채용공고 {rec_idx} 조회 중 예상치 못한 오류: {str(e)}")
            return None 