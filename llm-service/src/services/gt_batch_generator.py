import logging
import asyncio
import time
from typing import List, Dict, Tuple

from src.services.gt_agent import GTAgent
from src.services.backend_client import BackendClient


class GTBatchGenerator:
    """Ground Truth 샘플을 batch 로 생성·저장하는 서비스 레이어."""

    DEFAULT_CONCURRENCY = 5  # 동시 작업 개수 제한

    def __init__(self, agent: GTAgent | None = None, concurrency: int | None = None):
        self.agent = agent or GTAgent()
        self.logger = logging.getLogger(__name__)
        self.concurrency = concurrency or self.DEFAULT_CONCURRENCY

    async def _create_and_store_sample(self, idx: int, num_similar: int, sem: asyncio.Semaphore) -> Tuple[int | None, Dict[str, str] | None]:
        """단일 GT 샘플을 생성하고 저장한다. 성공 시 new_id 반환, 실패 시 error dict 반환."""
        async with sem:
            try:
                t0 = time.perf_counter()
                self.logger.info("[%d] GT 샘플 생성 시작", idx)

                # 1) 샘플 생성
                gt_data = await self.agent.create_sample(None, num_similar)

                # 2) 백엔드 저장
                async with BackendClient() as backend:
                    new_id = await backend.create_gt_sample(gt_data)

                elapsed = time.perf_counter() - t0
                self.logger.info("[%d] ✅ 완료 | id=%s | %.2fs", idx, new_id, elapsed)

                return new_id, None

            except Exception as e:
                self.logger.exception("[%d] ❌ 실패: %s", idx, str(e))
                return None, {"idx": idx, "detail": str(e)}

    async def generate(
        self, count: int, num_similar: int
    ) -> Tuple[List[int], List[Dict[str, str]]]:
        """GT 샘플을 count 개 생성하여 백엔드에 저장 (병렬 처리).

        Parameters
        ----------
        count : int
            생성할 샘플 개수
        num_similar : int
            관련 문서 개수 (GTAgent 인자)

        Returns
        -------
        ids : List[int]
            성공적으로 저장된 샘플 ID 목록
        errors : List[dict]
            실패한 항목의 인덱스 및 상세 오류 메시지
        """

        start_time = time.perf_counter()

        sem = asyncio.Semaphore(self.concurrency)

        tasks = [
            self._create_and_store_sample(idx + 1, num_similar, sem)
            for idx in range(count)
        ]

        results = await asyncio.gather(*tasks)

        ids: List[int] = []
        errors: List[Dict[str, str]] = []
        for new_id, err in results:
            if new_id is not None:
                ids.append(new_id)
            if err is not None:
                errors.append(err)

        elapsed_total = time.perf_counter() - start_time
        avg = elapsed_total / count if count else 0
        self.logger.info(
            "🎉 Batch GT 생성 완료 | 성공 %d | 실패 %d | 총 %.2fs | avg %.2fs",
            len(ids),
            len(errors),
            elapsed_total,
            avg,
        )

        return ids, errors 