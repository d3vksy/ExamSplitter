"""
설정 관리 모듈
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.models import ApplicationConfig, OutputFormat, ProcessingSettings
from ..utils.logger import get_logger
from ..utils.validators import (
    validate_confidence,
    validate_dpi,
    validate_group_size,
    validate_output_formats,
    validate_shuffle_seed,
)
from .defaults import DefaultSettings

logger = get_logger(__name__)


@dataclass
class UIConfig:
    """UI 관련 설정"""

    window_title: str = "ExamSplitter - PDF 시험지 문제 분할 도구"
    window_size: str = "1200x800"
    min_size: str = "1000x600"
    theme: str = "default"
    colors: Dict[str, str] = field(
        default_factory=lambda: {
            "primary": "#007bff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "info": "#17a2b8",
        }
    )


@dataclass
class ModelConfig:
    """모델 관련 설정"""

    default_model_path: Optional[Path] = None
    confidence_threshold: float = 0.3
    max_detections: int = 100
    supported_extensions: List[str] = field(
        default_factory=lambda: [".pt", ".pth", ".onnx", ".engine"]
    )


class SettingsManager:
    """설정 관리자 클래스"""

    def __init__(self) -> None:
        """설정 관리자를 초기화합니다."""
        self.logger = get_logger(__name__)

        # 중앙화된 기본값 사용
        self.app_config = self._create_default_app_config()
        self.processing_settings = self._create_default_processing_settings()
        self.ui_config = self._create_default_ui_config()
        self.model_config = self._create_default_model_config()

    def _create_default_app_config(self) -> ApplicationConfig:
        """기본 애플리케이션 설정을 생성합니다."""
        defaults = DefaultSettings.get_app_config_defaults()
        return ApplicationConfig(**defaults)

    def _create_default_processing_settings(self) -> ProcessingSettings:
        """기본 처리 설정을 생성합니다."""
        defaults = DefaultSettings.get_processing_defaults()
        return ProcessingSettings(**defaults)

    def _create_default_ui_config(self) -> UIConfig:
        """기본 UI 설정을 생성합니다."""
        defaults = DefaultSettings.get_ui_defaults()
        return UIConfig(**defaults)

    def _create_default_model_config(self) -> ModelConfig:
        """기본 모델 설정을 생성합니다."""
        defaults = DefaultSettings.get_model_defaults()
        return ModelConfig(**defaults)

    def get_processing_settings(self) -> ProcessingSettings:
        """현재 처리 설정을 반환합니다."""
        return self.processing_settings

    def get_app_config(self) -> ApplicationConfig:
        """현재 애플리케이션 설정을 반환합니다."""
        return self.app_config

    def update_app_config(self, **kwargs: Any) -> None:
        """애플리케이션 설정을 업데이트합니다."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.app_config, key):
                    setattr(self.app_config, key, value)

            self.logger.info("애플리케이션 설정 업데이트 완료")

        except Exception as e:
            self.logger.error(f"애플리케이션 설정 업데이트 실패: {e}")
            raise

    def update_processing_settings(self, **kwargs: Any) -> None:
        """처리 설정을 업데이트합니다."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.processing_settings, key):
                    # 값 검증
                    if key == "dpi":
                        value = validate_dpi(value)
                    elif key == "confidence":
                        value = validate_confidence(value)
                    elif key == "group_size":
                        value = validate_group_size(value)
                    elif key == "shuffle_seed":
                        value = validate_shuffle_seed(value)
                    elif key == "output_formats":
                        value = validate_output_formats(value)

                    setattr(self.processing_settings, key, value)

            self.logger.info("처리 설정 업데이트 완료")

        except Exception as e:
            self.logger.error(f"처리 설정 업데이트 실패: {e}")
            raise

    def get_ui_config(self) -> UIConfig:
        """현재 UI 설정을 반환합니다."""
        return self.ui_config

    def get_model_config(self) -> ModelConfig:
        """현재 모델 설정을 반환합니다."""
        return self.model_config

    def get_output_formats(self) -> Dict[str, OutputFormat]:
        """출력 형식 정보를 반환합니다."""
        formats = {}

        format_definitions = {
            "개별 이미지": OutputFormat(
                name="개별 이미지",
                description="각 문제를 개별 PNG 파일로 저장",
                file_extension=".png",
                icon="🖼️",
            ),
            "개별 PDF": OutputFormat(
                name="개별 PDF",
                description="각 문제를 개별 PDF 파일로 저장",
                file_extension=".pdf",
                icon="📄",
            ),
            "그룹 PDF": OutputFormat(
                name="그룹 PDF",
                description="문제들을 그룹으로 묶어 PDF 생성",
                file_extension=".pdf",
                icon="📚",
            ),
            "전체 문제집": OutputFormat(
                name="전체 문제집",
                description="모든 문제를 하나의 PDF로 통합",
                file_extension=".pdf",
                icon="📖",
            ),
            "셔플 문제집": OutputFormat(
                name="셔플 문제집",
                description="문제 순서를 섞어 PDF 생성",
                file_extension=".pdf",
                icon="🎲",
            ),
        }

        for name, enabled in self.processing_settings.output_formats.items():
            if name in format_definitions:
                format_info = format_definitions[name]
                format_info.enabled = enabled
                formats[name] = format_info

        return formats

    def reset_to_defaults(self) -> None:
        """설정을 기본값으로 초기화합니다."""
        try:
            self.app_config = self._create_default_app_config()
            self.processing_settings = self._create_default_processing_settings()
            self.ui_config = self._create_default_ui_config()
            self.model_config = self._create_default_model_config()

            self.logger.info("설정을 기본값으로 초기화했습니다")

        except Exception as e:
            self.logger.error(f"설정 초기화 실패: {e}")
            raise


# 전역 설정 관리자 인스턴스
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """전역 설정 관리자 인스턴스를 반환합니다."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_processing_settings() -> ProcessingSettings:
    """현재 처리 설정을 반환합니다."""
    return get_settings_manager().get_processing_settings()


def get_app_config() -> ApplicationConfig:
    """현재 애플리케이션 설정을 반환합니다."""
    return get_settings_manager().get_app_config()


def get_ui_config() -> UIConfig:
    """현재 UI 설정을 반환합니다."""
    return get_settings_manager().get_ui_config()


def get_model_config() -> ModelConfig:
    """현재 모델 설정을 반환합니다."""
    return get_settings_manager().get_model_config()
