"""
pdf 로드 및 이미지 확인"""

import os
from pathlib import Path
from typing import List


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
