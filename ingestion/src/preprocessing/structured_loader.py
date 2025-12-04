"""
StructuredDocumentLoader: JobPostParser 기반 구조화 문서 로더

섹션별 청크 생성 및 ChromaDB 메타데이터 관리
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import tempfile

from .job_post_parser import JobPostParser

logger = logging.getLogger(__name__)


class Chunk:
    """
    청크 데이터 클래스
    text + metadata로 구성
    metadata는 ChromaDB 저장용으로 설계됨

    원본 메타데이터 필드 보존:
    - deadline, start_date, crawling_time 등 원본 S3 JSON 메타데이터 전체 포함
    """

    def __init__(self, text: str, metadata: Dict[str, Any]):
        """
        Args:
            text: 청크 텍스트 (섹션 내용)
            metadata: ChromaDB 저장용 메타데이터
                - chunk_id (str): 고유 ID
                - rec_idx (str): 문서 ID
                - company (str): 회사명
                - title (str): 직무명
                - url (str): 상세 URL
                - section_type (str): 섹션 타입
                - section_length (int): 섹션 길이
                - tags (list): 태그 리스트
                - deadline (str): 마감일 (원본 메타데이터)
                - start_date (str): 모집 시작일 (원본 메타데이터)
                - crawling_time (str): 크롤링 시간 (원본 메타데이터)
                - 기타 원본 메타데이터 필드 전체 포함
        """
        self.text = text
        # 원본 메타데이터 전체 보존 (primitive 타입만)
        self.metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool, type(None)))
        }

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {"text": self.text, "metadata": self.metadata}

    def __repr__(self):
        return f"Chunk(chunk_id={self.metadata.get('chunk_id')}, section={self.metadata.get('section_type')}, length={len(self.text)})"


class StructuredDocumentLoader:
    """
    JobPostParser를 활용한 구조화 문서 로더

    특징:
    - 섹션별 청크 생성 (preferred, qualifications, job_duties)
    - ChromaDB 호환 메타데이터 자동 생성
    - 태그는 문서 레벨에서 추출 (모든 청크에 공유)
    - benefits, hiring_process, notes는 제외
    """

    # 임베딩 대상 섹션 (나머지는 제외)
    DEFAULT_TARGET_SECTIONS = ["preferred", "qualifications", "job_duties"]

    def __init__(
        self,
        strategy: str = "fast",
        target_sections: Optional[List[str]] = None,
        include_context: bool = True,
    ):
        """
        Args:
            strategy: unstructured 파싱 전략 ("fast", "hi_res")
            target_sections: 로드할 섹션 타입 리스트
                None이면 DEFAULT_TARGET_SECTIONS 사용
            include_context: JobPostParser의 context 주입 여부
        """
        self.parser = JobPostParser(strategy=strategy, include_context=include_context)
        self.target_sections = target_sections or self.DEFAULT_TARGET_SECTIONS
        self.chunks: List[Chunk] = []

        logger.info(f"✅ StructuredDocumentLoader 초기화")
        logger.info(f"   - 파싱 전략: {strategy}")
        logger.info(f"   - 대상 섹션: {', '.join(self.target_sections)}")
        logger.info(f"   - Context 주입: {include_context}")
