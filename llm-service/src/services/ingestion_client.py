import httpx
from typing import List, Optional

# Docker 프로덕션 환경과 동일하게 from src... 형태 사용
from src.api.models import RetrievalRequest, JobPosting
from src.config.config import settings
import logging

logger = logging.getLogger(__name__)


class IngestionClient:
    def __init__(self):
        self.base_url = settings.INGESTION_SERVICE_URL
        self.timeout = settings.INGESTION_REQUEST_TIMEOUT

    async def retrieve_documents(self, profile: RetrievalRequest) -> List[JobPosting]:
        """Ingestion 서비스에서 관련 문서를 검색합니다."""

        async with httpx.AsyncClient() as client:
            # Ingestion API 호출
            # Pydantic v2 호환성: model_dump() 우선 사용
            if hasattr(profile, 'model_dump'):
                profile_dict = profile.model_dump()
            elif hasattr(profile, 'dict'):
                profile_dict = profile.dict()
            else:
                profile_dict = dict(profile) if hasattr(profile, '__iter__') else {}
            
            response = await client.post(
                f"{self.base_url}/retrieval",
                json=profile_dict,
                timeout=self.timeout,
            )
            response.raise_for_status()

            # 응답 파싱
            response_data = response.json()
            documents_data = response_data.get("results", [])
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
                    content=doc_data.get("content", ""),
                )
                documents.append(job_posting)

            return documents

    async def get_similar_docs(self, seed_id: str, top_n: int = 10, pick_k: int = 4):
        """Ingestion 서비스에서 seed 기준 유사 문서(distance 포함) 목록을 받습니다."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/similar/{seed_id}",
                params={"top_n": top_n, "pick_k": pick_k},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json().get("candidates", [])

    async def get_all_ids(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/all-ids", timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()

    async def get_posting(self, rec_idx: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/post/{rec_idx}", timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
