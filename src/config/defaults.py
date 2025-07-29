"""
기본 설정값들을 중앙에서 관리하는 모듈
"""

from pathlib import Path
from typing import Dict, Any


class DefaultSettings:
    """기본 설정값들을 중앙에서 관리"""
    
    @staticmethod
    def get_project_root() -> Path:
        """프로젝트 루트 경로를 일관되게 반환"""
        return Path(__file__).parent.parent.parent
    
    @staticmethod
    def get_app_config_defaults() -> Dict[str, Any]:
        """애플리케이션 설정 기본값"""
        project_root = DefaultSettings.get_project_root()
        return {
            "project_root": project_root,
            "model_directory": project_root / "models",
            "output_directory": project_root / "outputs",
            "temp_directory": project_root / "temp",
            "log_level": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "max_workers": 1,
            "batch_size": 1
        }
    
    @staticmethod
    def get_processing_defaults() -> Dict[str, Any]:
        """처리 설정 기본값"""
        return {
            "dpi": 200,
            "confidence": 0.3,
            "group_size": 5,
            "max_file_size_mb": 50,
            "output_formats": {
                "개별 이미지": True,
                "개별 PDF": True,
                "그룹 PDF": False,
                "전체 문제집": False,
                "셔플 문제집": False
            },
            "shuffle_seed": None
        }
    
    @staticmethod
    def get_ui_defaults() -> Dict[str, Any]:
        """UI 설정 기본값"""
        return {
            "window_title": "ExamSplitter - PDF 시험지 문제 분할 도구",
            "window_size": "1200x800",
            "min_size": "1000x600",
            "theme": "default",
            "colors": {
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'info': '#17a2b8'
            }
        }
    
    @staticmethod
    def get_model_defaults() -> Dict[str, Any]:
        """모델 설정 기본값"""
        return {
            "default_model_path": None,
            "confidence_threshold": 0.3,
            "max_detections": 100,
            "supported_extensions": ['.pt', '.pth', '.onnx', '.engine']
        } 