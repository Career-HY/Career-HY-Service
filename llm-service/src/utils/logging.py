import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..config.config import settings


def setup_logging():
    """로깅 설정을 초기화합니다."""

    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 파일 핸들러 설정 (10MB 크기, 최대 5개 파일)
    file_handler = RotatingFileHandler(
        log_dir / "llm_service.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 서드파티 로거 레벨 조정
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
