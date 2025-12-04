"""
구조화된 채용공고 PDF 파서

Experiment 전략에 따라 PDF를 섹션별로 파싱합니다.
unstructured 라이브러리를 사용하여 preferred, qualifications, job_duties 섹션을 추출합니다.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JobPostParser:
    """
    채용공고 PDF를 구조화된 섹션으로 파싱하는 클래스

    Experiment 전략을 따라 섹션별 청킹을 위해 사용됩니다.
    """

    def __init__(self, strategy: str = "fast"):
        """
        JobPostParser 초기화

        Args:
            strategy: 파싱 전략 ("fast" | "hi_res")
                - "fast": 빠른 파싱 (약 10배 빠름, 프로덕션 권장)
                - "hi_res": 고해상도 파싱 (더 정확하지만 느림) -> 안쓰임 
        """
        if strategy not in ["fast", "hi_res"]:
            raise ValueError(f"strategy must be 'fast' or 'hi_res', got '{strategy}'")

        self.strategy = strategy
        logger.info(f"JobPostParser initialized with strategy: {strategy}")
