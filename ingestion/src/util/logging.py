import functools
import logging
import time
from typing import Callable
from datetime import datetime
import json


def setup_logging():
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def log_api_call(func: Callable) -> Callable:
    """API 엔드포인트의 호출을 로깅하는 데코레이터"""

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = logging.getLogger(f"api.{func.__name__}")
        start_time = time.time()

        # 요청 시작 로깅
        logger.info(
            f"API 호출 시작: {func.__name__}",
            extra={
                "event": "api_call_start",
                "function": func.__name__,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        try:
            # API 함수 실행
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 성공 로깅
            logger.info(
                f"API 호출 성공: {func.__name__}",
                extra={
                    "event": "api_call_success",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            # 에러 로깅 (traceback 포함)
            import traceback

            logger.error(f"API 호출 실패: {func.__name__}")
            logger.error(f"에러 타입: {type(e).__name__}")
            logger.error(f"에러 메시지: {str(e)}")
            logger.error(f"실행 시간: {round(execution_time, 3)}초")
            logger.error("=== Traceback ===")
            logger.error(traceback.format_exc())

            # 요청 인자 로깅 (디버깅용)
            if args:
                logger.error(f"요청 args: {args}")
            if kwargs:
                logger.error(f"요청 kwargs: {kwargs}")

            raise

    return async_wrapper
