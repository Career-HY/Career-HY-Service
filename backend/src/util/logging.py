import functools
import logging
import logging.handlers
import time
import json
import os
from datetime import datetime
from typing import Any, Callable
from fastapi import Request
import traceback

# 로거 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    
    # logs 디렉토리 생성
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # JSON 포맷터 (파일용 - 운영/분석용)
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "service": "backend",
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "message": record.getMessage()
            }
            
            # 추가 데이터가 있으면 포함
            if hasattr(record, 'extra_data'):
                log_entry.update(record.extra_data)
                
            return json.dumps(log_entry, ensure_ascii=False)
    
    # 사람이 읽기 쉬운 포맷터 (콘솔용 - 개발용)
    class ReadableFormatter(logging.Formatter):
        def format(self, record):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 기본 로그 형태
            base_msg = f"[{timestamp}] {record.levelname:8} | {record.module}.{record.funcName}:{record.lineno} | {record.getMessage()}"
            
            # 추가 데이터가 있으면 포함 (Event는 제외 - 이미 메시지에 포함됨)
            if hasattr(record, 'extra_data'):
                extra = record.extra_data
                if 'execution_time' in extra:
                    base_msg += f" | Time: {extra['execution_time']}s"
                if 'operation_type' in extra:
                    base_msg += f" | Operation: {extra['operation_type']}"
                if 'error_type' in extra:
                    base_msg += f" | Error: {extra['error_type']}"
                if 'error_message' in extra:
                    base_msg += f" | {extra['error_message']}"
                    
            return base_msg
    
    # 1. 일반 로그 파일 핸들러 (INFO 이상, 날짜별 분리)
    general_handler = logging.handlers.TimedRotatingFileHandler(
        filename='logs/backend.log',
        when='midnight',  # 자정마다 로테이션
        interval=1,       # 1일마다
        backupCount=30,   # 30일치 보관
        encoding='utf-8'
    )
    general_handler.setFormatter(JSONFormatter())
    general_handler.setLevel(logging.INFO)
    # 파일명에 날짜 형식 지정 (예: backend.log.2025-05-27)
    general_handler.suffix = "%Y-%m-%d"
    
    # 2. 에러 로그 파일 핸들러 (ERROR 이상만, 날짜별 분리)
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename='logs/backend-error.log',
        when='midnight',
        interval=1,
        backupCount=30,  
        encoding='utf-8'
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)
    error_handler.suffix = "%Y-%m-%d"
    
    # 콘솔 핸들러 (읽기 쉬운 형태로 출력)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ReadableFormatter())
    console_handler.setLevel(logging.DEBUG)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(general_handler)  # INFO 이상 로그
    root_logger.addHandler(error_handler)    # ERROR 이상 로그
    root_logger.addHandler(console_handler)  # 콘솔 출력
    
    return root_logger

# API 엔드포인트용 데코레이터
def log_api_call(func: Callable) -> Callable:
    """API 엔드포인트의 호출을 로깅합니다."""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(f"api.{func.__name__}")
        
        # 요청 정보 추출
        request_info = {}
        for arg in args:
            if isinstance(arg, Request):
                request_info = {
                    "method": arg.method,
                    "url": str(arg.url),
                    "client_ip": arg.client.host if arg.client else None,
                    "user_agent": arg.headers.get("user-agent", "")
                }
                break
        
        # 요청 시작 로깅
        api_path = request_info.get("url", "").split("?")[0] if request_info else ""
        method = request_info.get("method", "") if request_info else ""
        logger.info(f"API 호출 시작: {method} {api_path} ({func.__name__})", extra={
            "extra_data": {
                "event": "api_call_start",
                "function": func.__name__,
                "request_info": request_info,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
        })
        
        try:
            # 함수 실행
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # 성공 로깅
            logger.info(f"API 호출 성공: {method} {api_path} ({func.__name__})", extra={
                "extra_data": {
                    "event": "api_call_success",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "result_type": type(result).__name__
                }
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 에러 로깅
            logger.error("API 호출 실패", extra={
                "extra_data": {
                    "event": "api_call_error",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            })
            
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(f"api.{func.__name__}")
        
        # 요청 정보 추출 (sync에서는 Request 객체를 직접 접근하기 어려우므로 함수명만 사용)
        logger.info(f"API 호출 시작: {func.__name__}", extra={
            "extra_data": {
                "event": "api_call_start",
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
        })
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 성공 로깅
            logger.info(f"API 호출 성공: {func.__name__}", extra={
                "extra_data": {
                    "event": "api_call_success",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "result_type": type(result).__name__
                }
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 에러 로깅
            logger.error("API 호출 실패", extra={
                "extra_data": {
                    "event": "api_call_error",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            })
            
            raise
    
    # async 함수인지 확인
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# 데이터베이스 작업용 데코레이터
def log_db_operation(operation_type: str = "unknown"):
    """데이터베이스 작업을 로깅합니다."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(f"db.{func.__name__}")
            
            # 작업 시작 로깅
            logger.info(f"DB 작업 시작: {operation_type} - {func.__name__}", extra={
                "extra_data": {
                    "event": "db_operation_start",
                    "operation_type": operation_type,
                    "function": func.__name__
                }
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 성공 로깅
                logger.info(f"DB 작업 성공: {operation_type} - {func.__name__}", extra={
                    "extra_data": {
                        "event": "db_operation_success",
                        "operation_type": operation_type,
                        "function": func.__name__,
                        "execution_time": round(execution_time, 3)
                    }
                })
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # 에러 로깅
                logger.error("DB 작업 실패", extra={
                    "extra_data": {
                        "event": "db_operation_error",
                        "operation_type": operation_type,
                        "function": func.__name__,
                        "execution_time": round(execution_time, 3),
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                })
                
                raise
        
        return wrapper
    return decorator

# 일반 함수용 간단한 로깅 데코레이터
def log_function(func: Callable) -> Callable:
    """일반 함수의 실행을 로깅합니다."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(f"function.{func.__name__}")
        
        logger.info(f"함수 실행 시작: {func.__name__}", extra={
            "extra_data": {
                "event": "function_start",
                "function": func.__name__
            }
        })
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"함수 실행 완료: {func.__name__}", extra={
                "extra_data": {
                    "event": "function_success",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3)
                }
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error("함수 실행 실패", extra={
                "extra_data": {
                    "event": "function_error",
                    "function": func.__name__,
                    "execution_time": round(execution_time, 3),
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            })
            
            raise
    
    return wrapper 