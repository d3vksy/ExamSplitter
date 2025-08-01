"""
모델 관련 유틸리티 함수들
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


def get_model_directory() -> Path:
    """모델 디렉토리 경로를 반환합니다. exe 파일과 개발 환경 모두 지원합니다."""
    # 1. 현재 작업 디렉토리 기준으로 models 폴더 찾기
    current_dir = Path.cwd()
    model_dir = current_dir / "models"

    if model_dir.exists():
        return model_dir

    # 2. 스크립트 파일 기준으로 상대 경로 찾기
    script_dir = Path(__file__).parent.parent.parent
    model_dir = script_dir / "models"

    if model_dir.exists():
        return model_dir

    # 3. exe 파일 기준으로 상대 경로 찾기
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        model_dir = exe_dir / "models"

        if model_dir.exists():
            return model_dir

    # 찾지 못한 경우 기본 경로 반환
    return Path.cwd() / "models"


def get_model_path(model_name: str) -> Path:
    """모델 파일의 경로를 반환합니다."""
    model_dir = get_model_directory()
    return model_dir / model_name


def get_available_models() -> List[str]:
    """사용 가능한 모델 목록을 반환합니다."""
    model_dir = get_model_directory()

    if not model_dir.exists():
        return []

    models = []
    for model_file in model_dir.glob("*.pt"):
        models.append(model_file.name)

    return models


def get_model_info(model_name: str) -> Optional[dict]:
    """모델 정보를 반환합니다."""
    model_path = get_model_path(model_name)

    if not model_path.exists():
        return None

    size_mb = model_path.stat().st_size / (1024 * 1024)

    return {
        "name": model_path.name,
        "size_mb": f"{size_mb:.1f}",
        "path": str(model_path),
    }
