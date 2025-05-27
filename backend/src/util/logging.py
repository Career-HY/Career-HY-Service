import functools
import logging
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
    
    # JSON 포맷터
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
                
            return json.dumps(log_entry, ensure_ascii=False, indent=2)
    
    # 파일 핸들러
    file_handler = logging.FileHandler('logs/backend.log', encoding='utf-8')
    file_handler.setFormatter(JSONFormatter())
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러 (개발용)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    console_handler.setLevel(logging.DEBUG)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
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
        logger.info("API 호출 시작", extra={
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
            logger.info("API 호출 성공", extra={
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
        
        # 요청 시작 로깅
        logger.info("API 호출 시작", extra={
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
            logger.info("API 호출 성공", extra={
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
            logger.info("DB 작업 시작", extra={
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
                logger.info("DB 작업 성공", extra={
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
        
        logger.debug("함수 실행 시작", extra={
            "extra_data": {
                "event": "function_start",
                "function": func.__name__
            }
        })
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug("함수 실행 완료", extra={
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