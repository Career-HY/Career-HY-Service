import httpx
from typing import List, Optional
from src.api.models import RetrievalRequest, JobPosting
from src.config.config import settings
import logging

logger = logging.getLogger(__name__)


class IngestionClient:
    def __init__(self):
        self.base_url = settings.INGESTION_SERVICE_URL
        self.timeout = settings.INGESTION_REQUEST_TIMEOUT

    async def retrieve_documents(
        self, profile: RetrievalRequest, limit: Optional[int] = None
    ) -> List[JobPosting]:
        """Ingestion 서비스에서 관련 문서를 검색합니다."""
        
        async with httpx.AsyncClient() as client:
            # API 호출 - 올바른 엔드포인트와 요청 형식 사용
            response = await client.post(
                f"{self.base_url}/api/v1/retrieval",  # /retrieve → /retrieval로 수정
                json=profile.dict(),  # profile 래핑 제거, limit 제거
                timeout=self.timeout,
            )
            response.raise_for_status()

            # 응답 파싱 - 실제 응답 형식에 맞게 수정
            response_data = response.json()
            documents_data = response_data.get("results", [])  # documents → results

            # Dict를 JobPosting 객체로 변환
            documents = []
            for doc_data in documents_data:
                job_posting = JobPosting(
                    rec_idx=doc_data.get("rec_idx"),
                    title=doc_data.get("title", "제목 없음"),
                    url=doc_data.get("url", ""),
                    deadline=doc_data.get("deadline"),
                    start_date=doc_data.get("start_date"),
                    crawling_time=doc_data.get("crawling_time"),
                    content=doc_data.get("content", "")
                )
                documents.append(job_posting)

            return documents
