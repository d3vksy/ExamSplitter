"""
ExamSplitter 커스텀 예외 클래스들
"""

from typing import Optional


class ExamSplitterError(Exception):
    """ExamSplitter 기본 예외 클래스"""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ModelLoadError(ExamSplitterError):
    """모델 로드 관련 예외"""

    pass


class PDFProcessingError(ExamSplitterError):
    """PDF 처리 관련 예외"""

    pass


class ValidationError(ExamSplitterError):
    """입력 검증 관련 예외"""

    pass


class FileNotFoundError(ExamSplitterError):
    """파일을 찾을 수 없는 경우의 예외"""

    pass


class ConfigurationError(ExamSplitterError):
    """설정 관련 예외"""

    pass


class ProcessingError(ExamSplitterError):
    """처리 과정에서 발생하는 예외"""

    pass


class OutputGenerationError(ExamSplitterError):
    """출력 생성 관련 예외"""

    pass
