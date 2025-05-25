"""
pdf 로드 및 텍스트 추출 모듈
"""
import os
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def load_pdf_paths(pdf_dir: str) -> List[Path]:
    """
    지정된 폴더 내의 PDF 파일 경로들을 리스트로 반환합니다.
    """
    pdf_dir_path = Path(pdf_dir)
    if not pdf_dir_path.exists():
        raise FileNotFoundError(f"📁 PDF 폴더가 존재하지 않습니다: {pdf_dir}")

    pdf_paths = list(pdf_dir_path.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"⚠️ PDF 파일이 존재하지 않습니다: {pdf_dir}")

    print(f"✅ 총 {len(pdf_paths)}개의 PDF 파일을 불러왔습니다.")
    return pdf_paths


#PyMuPDF를 사용하여 PDF에서 텍스트 추출
def extract_text_PyMuPDF(pdf_path: Path) -> str:
    """
    PDF 파일에서 텍스트를 추출합니다.

    Args:
        pdf_path (Path): PDF 파일 경로

    Returns:
        str: 추출된 텍스트
    """
    text_list = []
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text_list.append(f"\n--- Page {page_num} ---\n")
                text_list.append(page.get_text())
            
    except Exception as e:
        logging.error(f"❌ {pdf_path.name} 텍스트 추출 실패: {e}")
        raise e  # 예외를 다시 발생시켜 호출자가 처리할 수 있도록 합니다.

    return ''.join(text_list)
