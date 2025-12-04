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
    청크 데이터 클래스 (text + metadata)
    - metadata: ChromaDB 저장용(PGVector/ChromaDB 등)으로 사용
    - 원본 S3 JSON의 전체 필드(deadline, start_date, crawling_time 등 포함)는
      청크별 메타데이터 생성 시(_create_chunks_from_parsed)에서 합쳐서 넣어줌
    - 여기서는 실제로 해당 딕셔너리 전체가 들어와도 primitive 타입(str/int/float/bool/None)만 보존
    """

    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        # primitive 타입 메타데이터 필드만 따로 추림 (embedding DB schema 호환)
        self.metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool, type(None)))
        }

    def to_dict(self) -> Dict[str, Any]:
        """dict로 변환 (embedding 저장용)"""
        return {"text": self.text, "metadata": self.metadata}

    def __repr__(self):
        return f"Chunk(chunk_id={self.metadata.get('chunk_id')}, section={self.metadata.get('section_type')}, length={len(self.text)})"


class StructuredDocumentLoader:
    """
    JobPostParser 기반 구조화 문서 로더

    - 섹션별 청크 생성(preferred/qualification/job_duties)
    - ChromaDB용 메타데이터 생성 구조에서 S3 원본 JSON 전체 dict까지 metadata에 포함시킴
    - Chunk는 primitive 타입만 보존하니 크기 부담 없이 활용 가능
    """

    DEFAULT_TARGET_SECTIONS = ["preferred", "qualifications", "job_duties"]

    def __init__(
        self,
        strategy: str = "fast",
        target_sections: Optional[List[str]] = None,
        include_context: bool = True,
    ):
        self.parser = JobPostParser(strategy=strategy, include_context=include_context)
        self.target_sections = target_sections or self.DEFAULT_TARGET_SECTIONS
        self.chunks: List[Chunk] = []

        logger.info(f"✅ StructuredDocumentLoader 초기화")
        logger.info(f"   - 파싱 전략: {strategy}")
        logger.info(f"   - 대상 섹션: {', '.join(self.target_sections)}")
        logger.info(f"   - Context 주입: {include_context}")

    @staticmethod
    def extract_company_and_title(text: str) -> tuple:
        """
        문서텍스트에서 회사명/직무명 추출 (간단 룰 기반: 관심기업 패턴/없는 경우 앞 2줄)
        """
        lines = text.split("\n")
        company = "미상"
        title = "미상"

        try:
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or "---" in line or "Page" in line:
                    continue

                if "관심기업" in line:
                    # 위쪽으로 회사명 추출
                    for j in range(i - 1, -1, -1):
                        prev_line = lines[j].strip()
                        if (
                            prev_line
                            and "---" not in prev_line
                            and "Page" not in prev_line
                        ):
                            company = prev_line
                            break
                    # 아래쪽으로 직무 타이틀 추출
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 5:
                            title = next_line
                            break
                    break
            if company == "미상":
                meaningful_lines = []
                for line in lines:
                    line = line.strip()
                    if (
                        line
                        and "---" not in line
                        and "Page" not in line
                        and len(line) > 2
                    ):
                        meaningful_lines.append(line)
                        if len(meaningful_lines) >= 2:
                            break
                if len(meaningful_lines) >= 1:
                    company = meaningful_lines[0]
                if len(meaningful_lines) >= 2:
                    title = meaningful_lines[1]
        except Exception as e:
            logger.warning(f"    ⚠️ 회사/직무 추출 실패: {e}")

        return company, title

    def _create_chunks_from_parsed(
        self,
        parsed_chunks: List[Dict[str, Any]],
        base_metadata: Dict[str, Any],
        raw_text: str = "",
    ) -> List[Chunk]:
        """
        JobPostParser 결과를 Chunk 객체로 변환.
        - S3 메타데이터(원본 전체 dict)는 base_metadata로 합쳐서 embedding에 쓸 수 있게 chunk_metadata에 미리 통합
        - 각 chunk 생성시 Chunk()로 전달 (init에서 primitive만 추려 유지)
        """
        doc_tags = []
        if parsed_chunks:
            doc_tags = parsed_chunks[0].get("metadata", {}).get("tags", [])
        chunks = []
        from collections import defaultdict
        section_counters = defaultdict(int)

        for parsed_chunk in parsed_chunks:
            section_type = parsed_chunk.get("metadata", {}).get(
                "section_type", "unknown"
            )
            if section_type not in self.target_sections:
                continue
            text = parsed_chunk.get("text", "")
            if not text or len(text.strip()) < 10:
                continue

            chunk_idx = section_counters[section_type]
            section_counters[section_type] += 1
            chunk_id = f"{base_metadata['rec_idx']}_{section_type}_{chunk_idx}"

            chunk_metadata = {
                **base_metadata,
                "chunk_id": chunk_id,
                "rec_idx": base_metadata["rec_idx"],
                "company": base_metadata.get("company") or base_metadata.get("company_name"),
                "title": base_metadata.get("title") or base_metadata.get("post_title"),
                "url": base_metadata.get("url") or base_metadata.get("detail_url"),
                "section_type": section_type,
                "section_length": len(text),
                "tags": doc_tags,
                "deadline": base_metadata.get("deadline"),
                "start_date": base_metadata.get("start_date"),
                "crawling_time": base_metadata.get("crawling_time"),
            }
            chunks.append(Chunk(text=text, metadata=chunk_metadata))

        if not chunks and raw_text:
            fallback_chunks = self._create_fallback_chunk(
                raw_text=raw_text, base_metadata=base_metadata, tags=doc_tags
            )
            chunks.extend(fallback_chunks)

            if len(fallback_chunks) == 1 and fallback_chunks[0].metadata.get(
                "is_lightweight"
            ):
                logger.info(f"   💡 경량 컨텍스트 생성: {base_metadata['rec_idx']}")
            else:
                logger.info(
                    f"   ✂️  Fallback 청킹 ({len(fallback_chunks)}개): {base_metadata['rec_idx']}"
                )

        return chunks
