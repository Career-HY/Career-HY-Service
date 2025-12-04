"""
구조화된 채용공고 PDF 파서

Experiment 전략에 따라 PDF를 섹션별로 파싱합니다.
unstructured 라이브러리를 사용하여 preferred, qualifications, job_duties 섹션을 추출합니다.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class JobPostParser:
    """
    PDF 형태 채용공고를 주어진 전략에 따라 섹션별로 파싱합니다.
    """

    def __init__(
        self,
        strategy: str = "fast",
        include_context: bool = True,
        min_section_length: int = 30,
    ):
        """
        JobPostParser를 초기화합니다.

        Args:
            strategy (str): 파싱 전략 ("fast" | "hi_res")
            include_context (bool): 각 청크에 회사명/직무명 컨텍스트 주입 여부
            min_section_length (int): 최소 섹션 길이 (너무 짧은 섹션 제외)
        """
        if strategy not in ("fast", "hi_res"):
            raise ValueError(f"strategy must be 'fast' or 'hi_res', got '{strategy}'")
        self.strategy = strategy
        self.include_context = include_context
        self.min_section_length = min_section_length

        # 채용공고 내 주요 섹션의 탐지 키워드
        self.section_keywords = {
            "company_intro": [
                "조직 소개",
                "팀소개",
                "회사 소개",
                "팀을 소개합니다",
                "회사소개",
                "조직소개",
                "Introduction",
                "ABOUT",
            ],
            "job_duties": [
                "담당업무",
                "주요업무",
                "이런 일을 하게",
                "함께 할 업무에요",
                "모집부문",
                "업무내용",
                "담당 업무",
                "주요 업무",
                "하실 일",
                "Responsibility",
                "responsibility",
                "responsibilities",
                "KEY PURPOSE OF ROLE",
            ],
            "qualifications": [
                "자격요건",
                "지원자격",
                "자격조건",
                "공통 자격요건",
                "이런 분을 찾고 있어요",
                "이런 분을 찾고",
                "필수 사항",
                "필수사항",
                "지원 자격",
                "자격 요건",
                "필수조건",
                "필수 조건",
                "자격",
                "requirement",
                "KEY RESPONSIBILITIES",
            ],
            "preferred": [
                "우대사항",
                "이런 분이면 더 좋아요",
                "이런 분이면",
                "우대 사항",
                "우대조건",
                "우대 조건",
                "우대 요건",
                "우대요건",
            ],
            "benefits": [
                "근무조건",
                "복리후생",
                "혜택 및 복지",
                "함께하면 받는 혜택 및 복지",
                "이런 혜택과 복지를",
                "근무 조건",
                "복리 후생",
                "혜택",
            ],
            "hiring_process": [
                "전형절차",
                "접수방법 및",
                "접수기간 및 방법",
                "제출서류",
                "이렇게 합류해요",
                "전형 절차",
                "제출 서류",
                "접수 방법",
            ],
            "notes": [
                "유의사항",
                "기타",
                "참고해 주세요",
                "채용서류 반환에 관한 고지",
                "유의 사항",
                "기타사항",
            ],
        }
        logger.info(f"JobPostParser initialized with strategy: {self.strategy}")

    def process_document(
        self, doc_path: str, original_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        메인 오케스트레이터: 문서 파싱 → 섹션 그룹화 → 청크 생성

        Args:
            doc_path: 문서 파일 경로 (PDF, DOCX 등)
            original_metadata: 원본 메타데이터
                - rec_idx (필수): 문서 고유 식별자
                - company (필수): 회사명
                - title (필수): 직무명

        Returns:
            청크 리스트 (각 청크는 text와 metadata 포함)
        """
        # 필수 필드 검증 (rec_idx 또는 rec_id 허용, 하위 호환성)
        rec_idx = original_metadata.get("rec_idx") or original_metadata.get("rec_id")
        if not rec_idx:
            raise ValueError("original_metadata must contain 'rec_idx' or 'rec_id'")

        required_fields = ["company", "title"]
        for field in required_fields:
            if field not in original_metadata:
                raise ValueError(f"original_metadata must contain '{field}'")

        # rec_idx가 없으면 rec_id를 rec_idx로 설정 (하위 호환성)
        if "rec_idx" not in original_metadata and "rec_id" in original_metadata:
            original_metadata["rec_idx"] = original_metadata["rec_id"]

        logger.info(f"\n{'='*70}")
        logger.info(f"📄 문서 처리: {original_metadata.get('rec_idx')}")
        logger.info(f"   회사: {original_metadata.get('company')}")
        logger.info(f"   직무: {original_metadata.get('title')}")
        logger.info(f"{'='*70}")

        # Step 1: 문서 파싱
        doc_path_obj = Path(doc_path)
        elements = self._parse_document(doc_path_obj)
        if not elements:
            logger.warning(f"⚠️ 문서 파싱 실패: {doc_path}")
            return []

        logger.info(f"✅ {len(elements)}개 elements 추출")

        # Step 2: 섹션 그룹화 및 태그 감지
        sections, tags = self._group_by_sections(elements)
        logger.info(f"✅ {len(sections)}개 섹션 감지")
        logger.info(f"✅ {len(tags)}개 태그 추출: {tags[:5]}...")  # 처음 5개만

        # Step 3: 메타데이터 업데이트
        doc_metadata = original_metadata.copy()
        doc_metadata["tags"] = tags

        # Step 4: 청크 생성 (후처리)
        chunks = self._sections_to_chunks(sections, doc_metadata)
        logger.info(f"✅ {len(chunks)}개 청크 생성")

        return chunks

    def _parse_document(self, doc_path: Path) -> Optional[List]:
        """
        문서 파싱: unstructured로 문서 로드

        Args:
            doc_path: 문서 파일 경로

        Returns:
            elements 리스트 또는 None
        """
        logger.debug(f"📥 문서 로드 중... (strategy: {self.strategy})")

        # PDF 파일인지 확인
        if doc_path.suffix.lower() == ".pdf":
            return self._parse_with_unstructured(doc_path)
        else:
            # 기타 파일 형식 (TXT 등) - 현재는 PDF만 지원
            logger.warning(f"⚠️ 지원하지 않는 파일 형식: {doc_path.suffix}")
            return None

    def _parse_with_unstructured(self, pdf_path: Path) -> Optional[list]:
        """
        unstructured 라이브러리를 사용해 PDF 파일을 파싱합니다.

        Args:
            pdf_path (Path): PDF 파일 경로

        Returns:
            list: unstructured elements 객체 리스트 또는 None(실패시)
        """
        try:
            from unstructured.partition.pdf import partition_pdf

            logger.debug(f"Parsing PDF with unstructured: {pdf_path.name}")

            elements = partition_pdf(
                filename=str(pdf_path),
                strategy=self.strategy,
                infer_table_structure=False,
            )
            logger.info(
                f"✅ Successfully parsed PDF: {pdf_path.name} ({len(elements)} elements)"
            )
            return elements
        except ImportError:
            logger.error("❌ unstructured library not installed")
        except Exception as e:
            logger.error(
                f"❌ Failed to parse PDF with unstructured: {pdf_path.name} - {e}"
            )
        return None

    def _normalize_text(self, text: str) -> str:
        """
        텍스트의 시작 부분 특수문자 및 불필요한 문자/공백 제거 등 단순화.

        Args:
            text (str): 원본 텍스트

        Returns:
            str: 정규화된 텍스트
        """
        # 줄 시작 부분 특수문자 및 괄호, 기호 제거
        normalized = re.sub(r"^[\[\]()■◆●▶◾▪*\s]+", "", text)
        # 앞뒤 공백/기호 추가 제거
        normalized = normalized.strip(" *-_[]()!?")
        return normalized

    def _detect_section(self, elem) -> Optional[str]:
        """
        (헤더) 텍스트로부터 해당 섹션 타입 반환

        Args:
            elem: unstructured Element 객체

        Returns:
            str | None: 표준 섹션명(ex. "job_duties")
        """
        if not hasattr(elem, "text") or not elem.text:
            return None

        normalized = self._normalize_text(elem.text)
        for section_type, keywords in self.section_keywords.items():
            for keyword in keywords:
                if normalized.startswith(keyword):
                    return section_type
        return None

    def _group_by_sections(self, elements: List) -> Tuple[Dict[str, List], List[str]]:
        """
        섹션별 그룹화 및 태그 감지

        각 element를 순회하며:
        1. #태그 감지 → detected_tags에 추가
        2. 섹션 헤더 감지 → current_section 업데이트
        3. 현재 섹션에 element 귀속

        Args:
            elements: unstructured elements 리스트

        Returns:
            (sections, tags) 튜플
            - sections: {section_type: [elem1, elem2, ...]}
            - tags: ["#태그1", "#태그2", ...]
        """
        sections = {}
        detected_tags = []
        current_section = "header"  # 기본 섹션

        for elem in elements:
            if not hasattr(elem, "text") or not elem.text or not elem.text.strip():
                continue

            text = elem.text.strip()

            # ========================================
            # [태그 감지 로직]
            # ========================================
            if text.startswith("#"):
                # 해당 라인의 모든 태그 추출
                tags_in_line = re.findall(r"#\S+", text)
                detected_tags.extend(tags_in_line)
                continue  # 태그는 섹션에 포함하지 않음

            # ========================================
            # [섹션 감지 로직]
            # ========================================
            detected_section = self._detect_section(elem)

            if detected_section:
                current_section = detected_section
                logger.debug(
                    f"   🔖 섹션 감지: {current_section} - '{elem.text[:40]}...'"
                )

            # ========================================
            # [섹션 귀속 로직]
            # ========================================
            # 키워드 미감지 시 current_section이 바뀌지 않으므로
            # 자동으로 header 또는 직전 섹션에 귀속됨
            if current_section not in sections:
                sections[current_section] = []

            sections[current_section].append(elem)

        # 중복 태그 제거
        unique_tags = list(set(detected_tags))

        logger.debug(f"✅ {len(sections)}개 섹션 감지, {len(unique_tags)}개 태그 추출")

        return sections, unique_tags

    def _sections_to_chunks(
        self, sections: Dict[str, List], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        섹션을 청크로 변환

        각 섹션에 대해:
        1. 컨텍스트 주입 (회사명, 직무명)
        2. Elements를 텍스트로 결합
        3. 최소 길이 체크
        4. 청크 딕셔너리 생성 (metadata 확장)

        Args:
            sections: 섹션별 elements 딕셔너리
            metadata: 문서 메타데이터 (rec_idx, company, title, tags 포함)

        Returns:
            청크 리스트 (각 청크는 text와 metadata 포함)
        """
        chunks = []

        # ========================================
        # [컨텍스트 주입]
        # ========================================
        company = metadata.get("company", "")
        title = metadata.get("title", "")

        context = ""
        if self.include_context and (company or title):
            context = f"[회사: {company}] [직무: {title}]\n\n"

        # 섹션별 청크 생성
        for section_type, elements in sections.items():
            # Elements를 텍스트로 결합
            section_text = "\n".join(
                [elem.text for elem in elements if elem.text and elem.text.strip()]
            )

            # 최소 길이 체크
            if len(section_text.strip()) < self.min_section_length:
                logger.debug(
                    f"   ⚠️ 섹션 '{section_type}' 너무 짧음 ({len(section_text)}자), 스킵"
                )
                continue

            # 컨텍스트 주입
            final_text = context + section_text if context else section_text

            # ========================================
            # [청크 딕셔너리 생성]
            # ========================================
            chunk = {
                "text": final_text,
                "metadata": {
                    **metadata,  # rec_idx, company, title, tags 포함
                    "section_type": section_type,
                    "section_length": len(section_text),
                    "chunk_method": "structured_parsing",
                    "has_context": self.include_context,
                },
            }

            chunks.append(chunk)
            logger.debug(f"   ✅ Chunk 생성: {section_type} ({len(section_text)}자)")

        return chunks

    def _extract_sections(self, elements: list) -> Dict[str, str]:
        """
        unstructured에서 파싱된 elements에서 주요 섹션별로 텍스트를 추출.

        Args:
            elements (list): unstructured elements 리스트

        Returns:
            dict: {
                "preferred": str,
                "qualifications": str,
                "job_duties": str,
                "full_text": str
            }
        """
        # 주요 섹션만 미리 빈 문자열로 세팅
        sections = {
            "preferred": "",
            "qualifications": "",
            "job_duties": "",
            "full_text": "",
        }
        full_text_parts = []

        current_section = None
        current_text = []
        for element in elements:
            if not hasattr(element, "text") or not element.text:
                continue
            text = element.text.strip()
            if not text:
                continue

            full_text_parts.append(text)

            # 새 섹션 헤더 감지 (텍스트가 짧고, 키워드를 포함하면 헤더로 간주)
            text_lower = text.lower()
            found_header = False
            for section_name, keywords in self.section_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower and len(text) < 100:
                        if current_section and current_text:
                            sections[current_section] = "\n".join(current_text).strip()
                        current_section = section_name
                        current_text = []
                        found_header = True
                        break
                if found_header:
                    break

            # 새 섹션이거나 기존 섹션 지속
            if current_section:
                current_text.append(text)

        # 마지막 남은 섹션(마지막 섹션) 반영
        if current_section and current_text:
            sections[current_section] = "\n".join(current_text).strip()

        sections["full_text"] = "\n".join(full_text_parts).strip()

        logger.debug(
            f"Extracted sections - preferred: {len(sections['preferred'])} chars, "
            f"qualifications: {len(sections['qualifications'])} chars, "
            f"job_duties: {len(sections['job_duties'])} chars"
        )
        return sections
