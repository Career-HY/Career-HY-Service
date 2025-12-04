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
            k: v for k, v in metadata.items()
            if isinstance(v, (str, int, float, bool, type(None)))
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
                        if prev_line and "---" not in prev_line and "Page" not in prev_line:
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
                meaningful_lines = [
                    line.strip() for line in lines
                    if line.strip() and "---" not in line and "Page" not in line and len(line.strip()) > 2
                ]
                if meaningful_lines:
                    company = meaningful_lines[0]
                if len(meaningful_lines) > 1:
                    title = meaningful_lines[1]
        except Exception as e:
            logger.warning(f"    ⚠️ 회사/직무 추출 실패: {e}")

        return company, title

    def _get_base_metadata(self, doc_metadata, raw_text, idx=0):
        # raw_text에서 회사명과 직무명 추출 (메타데이터에 없을 때만)
        company, title = self.extract_company_and_title(raw_text)
        rec_id = doc_metadata.get("rec_idx", f"unknown_{idx}")

        base_metadata = {
            **doc_metadata,
            "rec_idx": str(rec_id),
            "title": (
                doc_metadata.get("title")
                or doc_metadata.get("post_title")
                or title
            ),
            "company": (
                doc_metadata.get("company")
                or doc_metadata.get("company_name")
                or company
            ),
            "url": (
                doc_metadata.get("url")
                or doc_metadata.get(
                    "detail_url",
                    f"https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=public-recruit&rec_idx={rec_id}",
                )
            ),
            # 원본 필드명도 명시적으로 보존 (하위 호환성)
            "post_title": (
                doc_metadata.get("post_title")
                or doc_metadata.get("title")
                or title
            ),
            "company_name": (
                doc_metadata.get("company_name")
                or doc_metadata.get("company")
                or company
            ),
            "detail_url": (
                doc_metadata.get("detail_url")
                or doc_metadata.get("url")
                or ""
            ),
        }

        # S3 JSON 메타데이터 필드명 매핑 (필요한 경우)
        for key in ["deadline", "start_date", "crawling_time"]:
            if key not in base_metadata or base_metadata.get(key) is None:
                base_metadata[key] = doc_metadata.get(key)

        return base_metadata

    def _chunk_common_metadata(self, base_metadata, section_type, text, doc_tags, chunk_id, extra=None):
        """
        중복되는 chunk metadata 생성 로직 공통화
        """
        metadata = {
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
        if extra:
            metadata.update(extra)
        return metadata

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
        doc_tags = parsed_chunks[0].get("metadata", {}).get("tags", []) if parsed_chunks else []
        from collections import defaultdict
        section_counters = defaultdict(int)
        chunks = []

        for parsed_chunk in parsed_chunks:
            section_type = parsed_chunk.get("metadata", {}).get("section_type", "unknown")
            if section_type not in self.target_sections:
                continue
            text = parsed_chunk.get("text", "")
            if not text or len(text.strip()) < 10:
                continue
            chunk_idx = section_counters[section_type]
            section_counters[section_type] += 1
            chunk_id = f"{base_metadata['rec_idx']}_{section_type}_{chunk_idx}"

            chunk_metadata = self._chunk_common_metadata(
                base_metadata, section_type, text, doc_tags, chunk_id
            )
            chunks.append(Chunk(text=text, metadata=chunk_metadata))

        if not chunks and raw_text:
            fallback_chunks = self._create_fallback_chunk(
                raw_text=raw_text, base_metadata=base_metadata, tags=doc_tags
            )
            chunks.extend(fallback_chunks)
            if len(fallback_chunks) == 1 and fallback_chunks[0].metadata.get("is_lightweight"):
                logger.info(f"   💡 경량 컨텍스트 생성: {base_metadata['rec_idx']}")
            else:
                logger.info(f"   ✂️  Fallback 청킹 ({len(fallback_chunks)}개): {base_metadata['rec_idx']}")

        return chunks

    def _create_fallback_chunk(
        self, raw_text: str, base_metadata: Dict[str, Any], tags: List[str]
    ) -> List[Chunk]:
        """
        Target 섹션이 없을 때 fallback 청크 생성

        하이브리드 접근:
        - 900자 이하: 경량 컨텍스트 (회사+직무+태그만)
        - 900자 초과: 400자 단위 청킹
        """
        max_raw_length = 2000
        truncated_raw_text = raw_text[:max_raw_length]

        # Context 추가한 전체 텍스트
        full_text_with_context = (
            f"[회사: {base_metadata['company']}] "
            f"[직무: {base_metadata['title']}]\n\n"
            f"{truncated_raw_text}"
        )
        text_length = len(full_text_with_context)

        # 900자 이하: 경량 컨텍스트 생성
        if text_length <= 900:
            lightweight_lines = [
                f"회사: {base_metadata['company']}",
                f"직무: {base_metadata['title']}"
            ]
            if tags:
                tags_str = ", ".join(tags[:5])
                if len(tags) > 5:
                    tags_str += f" 외 {len(tags)-5}개"
                lightweight_lines.append(f"태그: {tags_str}")

            lightweight_text = "\n".join(lightweight_lines)
            chunk_id = f"{base_metadata['rec_idx']}_full_text_0"
            chunk_metadata = self._chunk_common_metadata(
                base_metadata, "full_text", lightweight_text, tags, chunk_id, extra={
                    "is_fallback": True,
                    "is_lightweight": True,
                }
            )

            return [Chunk(text=lightweight_text, metadata=chunk_metadata)]

        # 900자 초과: 400자 단위 청킹
        else:
            chunks = []
            chunk_size = 400
            num_chunks = (text_length + chunk_size - 1) // chunk_size

            for i in range(num_chunks):
                start_idx = i * chunk_size
                end_idx = min(start_idx + chunk_size, text_length)
                chunk_text = full_text_with_context[start_idx:end_idx]
                chunk_id = f"{base_metadata['rec_idx']}_full_text_{i}"
                chunk_metadata = self._chunk_common_metadata(
                    base_metadata, "full_text", chunk_text, tags, chunk_id, extra={
                        "is_fallback": True,
                        "chunk_index": i,
                        "total_chunks": num_chunks,
                    }
                )
                chunks.append(Chunk(text=chunk_text, metadata=chunk_metadata))
            return chunks

    def load_from_documents(
        self, documents: List[Dict[str, Any]], limit: Optional[int] = None
    ) -> List[Chunk]:
        """
        메모리에 이미 로드된 documents 리스트에서 바로 파싱 및 청크 생성

        Args:
            documents: S3DataLoader.load_documents() 형태의 리스트 (각 원소: {"text": str, "metadata": dict})
            limit: 처리할 문서 수 제한 (None이면 전체)
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📂 메모리 문서 리스트에서 구조화 파싱 시작 (JobPostParser + unstructured)")
        logger.info(f"{'='*80}")

        total_docs = len(documents)
        process_count = limit if limit else total_docs

        logger.info(f"✅ 총 문서: {total_docs}개")
        logger.info(f"🎯 처리 대상: {process_count}개")
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 문서 파싱 시작 (in-memory)")
        logger.info(f"{'='*80}\n")

        self.chunks = []
        failed_docs = []
        docs_to_process = documents[:process_count]

        for idx, doc_item in enumerate(docs_to_process):
            try:
                doc_metadata = doc_item.get("metadata", {})
                raw_text = doc_item.get("text", "")
                rec_id = doc_metadata.get("rec_idx", f"unknown_{idx}")

                # base_metadata 생성 (중복 제거)
                base_metadata = self._get_base_metadata(doc_metadata, raw_text, idx)

                if idx == 0:
                    # 첫번째 문서의 메타데이터 확인
                    logger.info(f"\n🔍 첫 번째 문서 메타데이터 확인 (rec_idx: {rec_id}):")
                    for key in ["deadline", "start_date", "crawling_time", "post_title", "company_name"]:
                        logger.info(f"   - {key}: {doc_metadata.get(key)}")
                    logger.info(f"   - 전체 메타데이터 키: {list(doc_metadata.keys())[:20]}")

                # 텍스트 검증
                if not raw_text or len(raw_text) < 50:
                    failed_docs.append((rec_id, "텍스트 없음"))
                    continue

                # 임시 파일로 저장하여 JobPostParser 사용 (unstructured 기반)
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False, encoding="utf-8"
                ) as tmp_file:
                    tmp_file.write(raw_text)
                    tmp_path = tmp_file.name

                parsed_chunks = self.parser.process_document(
                    doc_path=tmp_path, original_metadata=base_metadata
                )
                Path(tmp_path).unlink()

                doc_chunks = self._create_chunks_from_parsed(
                    parsed_chunks, base_metadata=base_metadata, raw_text=raw_text
                )
                self.chunks.extend(doc_chunks)

            except Exception as e:
                error_msg = str(e)
                import traceback

                if idx < 3:  # 처음 3개만 상세 에러 출력
                    logger.error(f"\n❌ 문서 {idx} 파싱 실패 (rec_idx: {rec_id}):")
                    logger.error(f"   에러: {error_msg}")
                    logger.error(f"   상세:")
                    traceback.print_exc()
                failed_docs.append((rec_id, error_msg))
                continue

        logger.info(f"\n{'='*80}")
        logger.info(f"✅ in-memory 파싱 완료")
        logger.info(f"{'='*80}")
        logger.info(f"📊 총 청크 수: {len(self.chunks)}개")
        logger.info(f"❌ 실패 문서: {len(failed_docs)}개")

        if failed_docs:
            logger.info(f"\n실패 문서 목록 (최대 20개):")
            for rec_id, reason in failed_docs[:20]:
                logger.info(f"  - {rec_id}: {reason}")
            if len(failed_docs) > 20:
                logger.info(f"  ... 외 {len(failed_docs) - 20}개 실패")

        return self.chunks
