import httpx
from typing import List, Dict, Optional
from src.api.models import RetrievalRequest
from src.config.config import settings
from fastapi import HTTPException
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# 로거 설정
logger = logging.getLogger(__name__)


class IngestionClientError(Exception):
    """Ingestion 클라이언트 관련 에러"""

    pass


class IngestionClient:
    def __init__(self):
        self.base_url = settings.INGESTION_SERVICE_URL
        self.timeout = settings.INGESTION_REQUEST_TIMEOUT

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_cls=IngestionClientError,
    )
    async def retrieve_documents(
        self, profile: RetrievalRequest, limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Ingestion 서비스에서 관련 문서를 검색합니다.

        Args:
            profile (RetrievalRequest): 사용자 프로필 정보
            limit (Optional[int]): 반환할 최대 문서 수

        Returns:
            List[Dict]: 검색된 문서 목록

        Raises:
            IngestionClientError: Ingestion 서비스 호출 중 에러 발생 시
        """
        try:
            async with httpx.AsyncClient() as client:
                # 요청 데이터 준비
                request_data = {
                    "profile": profile.dict(),
                    "limit": limit or settings.MAX_DOCUMENTS,
                }

                # API 호출
                response = await client.post(
                    f"{self.base_url}/api/v1/retrieve",
                    json=request_data,
                    timeout=self.timeout,
                )

                # 응답 검증
                if response.status_code == 404:
                    logger.warning("No documents found for the given profile")
                    return []

                if response.status_code != 200:
                    error_msg = f"Ingestion service error: {response.text}"
                    logger.error(error_msg)
                    if response.status_code >= 500:
                        raise IngestionClientError(
                            f"Ingestion service internal error: {response.status_code}"
                        )
                    else:
                        raise HTTPException(
                            status_code=response.status_code, detail=error_msg
                        )

                # 응답 파싱
                response_data = response.json()
                documents = response_data.get("documents", [])

                # 문서 검증
                if not isinstance(documents, list):
                    raise IngestionClientError(
                        "Invalid response format: documents should be a list"
                    )

                # 메타데이터 로깅
                metadata = response_data.get("metadata", {})
                logger.info(
                    "Retrieved %d documents. Search time: %s ms",
                    len(documents),
                    metadata.get("search_time_ms", "N/A"),
                )

                return documents

        except httpx.TimeoutException:
            error_msg = f"Request to ingestion service timed out after {self.timeout}s"
            logger.error(error_msg)
            raise IngestionClientError(error_msg)

        except httpx.RequestError as e:
            error_msg = f"Failed to connect to ingestion service: {str(e)}"
            logger.error(error_msg)
            raise IngestionClientError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error while retrieving documents: {str(e)}"
            logger.error(error_msg)
            raise IngestionClientError(error_msg)

    async def health_check(self) -> bool:
        """
        Ingestion 서비스의 상태를 확인합니다.

        Returns:
            bool: 서비스가 정상적으로 동작하는지 여부
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
