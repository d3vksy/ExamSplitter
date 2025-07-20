"""
설정 모듈 초기화
"""

# 기본 설정 상수들
DEFAULT_DPI = 200
DEFAULT_CONFIDENCE = 0.3
DEFAULT_GROUP_SIZE = 5

# 설정 관리자 함수들
from .settings import (
    get_settings_manager,
    get_processing_settings,
    get_ui_config,
    get_model_config
)

# 모델 관련 함수들 (임시 구현)
def get_available_models():
    """사용 가능한 모델 목록을 반환합니다."""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    model_dir = project_root / "models"
    
    if not model_dir.exists():
        return []
    
    models = []
    for model_file in model_dir.glob("*.pt"):
        models.append(str(model_file))
    
    return models

def get_model_info(model_path):
    """모델 정보를 반환합니다."""
    from pathlib import Path
    import os
    
    path = Path(model_path)
    if not path.exists():
        return None
    
    size_mb = path.stat().st_size / (1024 * 1024)
    
    return {
        'name': path.name,
        'size_mb': f"{size_mb:.1f}",
        'path': str(path)
    }
