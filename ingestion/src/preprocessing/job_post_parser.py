"""
구조화된 채용공고 PDF 파서

Experiment 전략에 따라 PDF를 섹션별로 파싱합니다.
unstructured 라이브러리를 사용하여 preferred, qualifications, job_duties 섹션을 추출합니다.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class JobPostParser:
    """
    PDF 형태 채용공고를 주어진 전략에 따라 섹션별로 파싱합니다.
    """

    def __init__(self, strategy: str = "fast"):
        """
        JobPostParser를 초기화합니다.

        Args:
            strategy (str): 파싱 전략 ("fast" | "hi_res")
        """
        if strategy not in ("fast", "hi_res"):
            raise ValueError(f"strategy must be 'fast' or 'hi_res', got '{strategy}'")
        self.strategy = strategy

        # 채용공고 내 주요 섹션의 탐지 키워드
        self.section_keywords = {
            "company_intro": [
                "조직 소개", "팀소개", "회사 소개", "팀을 소개합니다", "회사소개", "조직소개", "Introduction", "ABOUT",
            ],
            "job_duties": [
                "담당업무", "주요업무", "이런 일을 하게", "함께 할 업무에요", "모집부문", "업무내용",
                "담당 업무", "주요 업무", "하실 일", "Responsibility", "responsibility",
                "responsibilities", "KEY PURPOSE OF ROLE",
            ],
            "qualifications": [
                "자격요건", "지원자격", "자격조건", "공통 자격요건", "이런 분을 찾고 있어요", "이런 분을 찾고",
                "필수 사항", "필수사항", "지원 자격", "자격 요건", "필수조건", "필수 조건", "자격",
                "requirement", "KEY RESPONSIBILITIES",
            ],
            "preferred": [
                "우대사항", "이런 분이면 더 좋아요", "이런 분이면", "우대 사항", "우대조건", "우대 조건", "우대 요건", "우대요건",
            ],
            "benefits": [
                "근무조건", "복리후생", "혜택 및 복지", "함께하면 받는 혜택 및 복지",
                "이런 혜택과 복지를", "근무 조건", "복리 후생", "혜택",
            ],
            "hiring_process": [
                "전형절차", "접수방법 및", "접수기간 및 방법", "제출서류", "이렇게 합류해요",
                "전형 절차", "제출 서류", "접수 방법",
            ],
            "notes": [
                "유의사항", "기타", "참고해 주세요", "채용서류 반환에 관한 고지", "유의 사항", "기타사항",
            ],
        }
        logger.info(f"JobPostParser initialized with strategy: {self.strategy}")

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
