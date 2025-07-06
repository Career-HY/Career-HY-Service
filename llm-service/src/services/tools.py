from __future__ import annotations

from typing import Any
from langchain.tools import StructuredTool
import httpx
from src.config.config import settings
from src.services.ingestion_client import IngestionClient
import asyncio


async def _get_job_posting_async(rec_idx: str):
    client = IngestionClient()
    return await client.get_posting(rec_idx)

def _get_job_posting(rec_idx: str):
    """동기 Wrapper – async 함수 실행 후 결과 반환"""
    return asyncio.run(_get_job_posting_async(rec_idx))

job_posting_tool = StructuredTool.from_function(
    _get_job_posting,
    name="get_job_posting",
    description="rec_idx로 채용공고 메타데이터와 요약을 가져옵니다.",
    coroutine=_get_job_posting_async,
)

async def _search_course_async(q: str, limit: int = 1):
    """백엔드 수강편람 검색 API를 호출하여 과목 정보를 반환합니다."""
    url = f"{settings.BACKEND_API_URL}/courses/search"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"q": q, "limit": limit})
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return {"error": f"NO_RESULTS for keyword '{q}'"}
        return data

def _search_course(q: str, limit: int = 1):
    data = asyncio.run(_search_course_async(q=q, limit=limit))
    if not data:
        return {"error": f"NO_RESULTS for keyword '{q}'"}
    return data

course_search_tool = StructuredTool.from_function(
    _search_course,
    name="search_course_catalog",
    description="키워드(과목명 또는 개설학과)로 대학 수강편람을 검색하여 과목 정보를 반환합니다.",
    coroutine=_search_course_async,
) 