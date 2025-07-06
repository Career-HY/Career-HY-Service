from __future__ import annotations

import httpx
from typing import Any, Dict

from src.config.config import settings


class BackendClient:
    """백엔드(GT 저장 API) 호출 클라이언트."""

    def __init__(self):
        self._base = settings.BACKEND_API_URL.rstrip("/")
        self._api_key = settings.ADMIN_API_KEY
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20.0)
        return self._client

    async def create_gt_sample(self, sample: Dict[str, Any]) -> int:
        """백엔드 /gt-samples POST 호출하여 샘플을 저장하고 ID를 반환합니다."""
        client = await self._get_client()
        headers = {}
        if self._api_key:
            headers["X-API-Key"] = self._api_key

        resp = await client.post(
            f"{self._base}/gt-samples",
            json=sample,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # context manager 지원
    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close() 