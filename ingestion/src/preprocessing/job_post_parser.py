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
    
    def _parse_with_unstructured(self, pdf_path: Path) -> Optional[list]:
        """
        unstructured 라이브러리를 사용하여 PDF를 파싱합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            unstructured elements 리스트 또는 None (실패 시)
        """
        try:
            from unstructured.partition.pdf import partition_pdf
            
            logger.debug(f"Parsing PDF with unstructured: {pdf_path.name}")
            
            # unstructured로 PDF 파싱
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy=self.strategy,
                infer_table_structure=False,  # 테이블 구조 추론 비활성화 (속도 향상)
            )
            
            logger.info(f"✅ Successfully parsed PDF: {pdf_path.name} ({len(elements)} elements)")
            return elements
            
        except ImportError:
            logger.error("❌ unstructured library not installed")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to parse PDF with unstructured: {pdf_path.name} - {e}")
            return None
