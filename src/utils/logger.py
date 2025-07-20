"""
로깅 유틸리티 모듈
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """로깅 설정을 초기화합니다.
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 로그 포맷 문자열
        log_file: 로그 파일 경로 (None이면 파일 로깅 비활성화)
        console_output: 콘솔 출력 여부
        
    Returns:
        설정된 로거 인스턴스
    """
    # 로그 레벨 변환
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"유효하지 않은 로그 레벨: {log_level}")
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 포맷터 생성
    formatter = logging.Formatter(log_format)
    
    # 콘솔 핸들러
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 파일 핸들러
    if log_file:
        # 로그 디렉토리 생성
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """지정된 이름의 로거를 반환합니다.
    
    Args:
        name: 로거 이름
        
    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)


class ProcessingLogger:
    """처리 과정을 추적하는 전용 로거"""
    
    def __init__(self, name: str = "ExamSplitter"):
        self.logger = get_logger(name)
        self.start_time = None
        self.step_count = 0
    
    def start_processing(self, operation: str) -> None:
        """처리 시작을 로깅합니다."""
        self.start_time = datetime.now()
        self.step_count = 0
        self.logger.info(f"{operation} 시작")
    
    def log_step(self, step: str, details: Optional[str] = None) -> None:
        """처리 단계를 로깅합니다."""
        self.step_count += 1
        message = f"단계 {self.step_count}: {step}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_progress(self, current: int, total: int, description: str = "") -> None:
        """진행 상황을 로깅합니다."""
        percentage = (current / total) * 100 if total > 0 else 0
        message = f"진행률: {current}/{total} ({percentage:.1f}%)"
        if description:
            message += f" - {description}"
        self.logger.info(message)
    
    def log_success(self, message: str) -> None:
        """성공 메시지를 로깅합니다."""
        self.logger.info(f"성공 : {message}")
    
    def log_warning(self, message: str) -> None:
        """경고 메시지를 로깅합니다."""
        self.logger.warning(f"경고 : {message}")
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """오류 메시지를 로깅합니다."""
        if error:
            self.logger.error(f"오류: {message}: {error}", exc_info=True)
        else:
            self.logger.error(f"오류: {message}")
    
    def finish_processing(self, operation: str, success: bool = True) -> None:
        """처리 완료를 로깅합니다."""
        if self.start_time:
            duration = datetime.now() - self.start_time
            duration_str = str(duration).split('.')[0]  # 마이크로초 제거
            
            if success:
                self.logger.info(f"{operation} 완료 (소요시간: {duration_str})")
            else:
                self.logger.error(f"{operation} 실패 (소요시간: {duration_str})")
        else:
            if success:
                self.logger.info(f"{operation} 완료")
            else:
                self.logger.error(f"{operation} 실패")


def log_function_call(func):
    """함수 호출을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"함수 호출: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"함수 완료: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"함수 오류: {func.__name__} - {e}")
            raise
    return wrapper


def log_execution_time(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        logger.debug(f"함수 시작: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = end_time - start_time
            logger.debug(f"함수 완료: {func.__name__} (소요시간: {duration})")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = end_time - start_time
            logger.error(f"함수 오류: {func.__name__} (소요시간: {duration}) - {e}")
            raise
    return wrapper 