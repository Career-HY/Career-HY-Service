import logging
from typing import List, Dict, Tuple

from src.services.gt_agent import GTAgent
from src.services.backend_client import BackendClient


class GTBatchGenerator:
    """Ground Truth 샘플을 batch 로 생성·저장하는 서비스 레이어."""

    def __init__(self, agent: GTAgent | None = None):
        self.agent = agent or GTAgent()
        self.logger = logging.getLogger(__name__)

    async def generate(
        self, count: int, num_similar: int
    ) -> Tuple[List[int], List[Dict[str, str]]]:
        """GT 샘플을 count 개 생성하여 백엔드에 저장.

        Returns
        -------
        ids : List[int]
            성공적으로 저장된 샘플 ID 목록
        errors : List[dict]
            실패한 항목의 인덱스 및 상세 오류 메시지
        """
        ids: List[int] = []
        errors: List[Dict[str, str]] = []

        for idx in range(count):
            try:
                self.logger.info("[%d/%d] GT 샘플 생성 시작", idx + 1, count)

                # 1. 샘플 생성
                gt_data = await self.agent.create_sample(None, num_similar)

                # 2. 백엔드 저장
                async with BackendClient() as backend:
                    new_id = await backend.create_gt_sample(gt_data)

                ids.append(new_id)
                self.logger.info(
                    "[%d/%d] ✅ 저장 완료 | id=%s", idx + 1, count, new_id
                )

            except Exception as e:
                self.logger.exception(
                    "[%d/%d] ❌ 실패: %s", idx + 1, count, str(e)
                )
                errors.append({"idx": idx, "detail": str(e)})

        return ids, errors 