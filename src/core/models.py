"""
ExamSplitter 데이터 모델 클래스들
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime


@dataclass
class DetectionResult:
    """문제 감지 결과를 담는 데이터 클래스"""
    
    question_id: str
    page_number: int
    bounding_box: Tuple[float, float, float, float]  # x1, y1, x2, y2
    confidence: float
    image_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """데이터 검증"""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("신뢰도는 0.0-1.0 범위여야 합니다")
        
        if self.page_number < 1:
            raise ValueError("페이지 번호는 1 이상이어야 합니다")
        
        if len(self.bounding_box) != 4:
            raise ValueError("바운딩 박스는 4개의 값이 필요합니다")


@dataclass
class ProcessingSettings:
    """처리 설정을 담는 데이터 클래스"""
    
    dpi: int = 200
    confidence: float = 0.3
    group_size: int = 5
    max_file_size_mb: int = 50
    output_formats: Dict[str, bool] = field(default_factory=dict)
    shuffle_seed: Optional[int] = None
    
    def __post_init__(self):
        """데이터 검증"""
        if not (150 <= self.dpi <= 600):
            raise ValueError("DPI는 150-600 범위여야 합니다")
        
        if not (0.1 <= self.confidence <= 1.0):
            raise ValueError("신뢰도는 0.1-1.0 범위여야 합니다")
        
        if not (1 <= self.group_size <= 20):
            raise ValueError("그룹 크기는 1-20 범위여야 합니다")
        
        if self.shuffle_seed is not None and not (1 <= self.shuffle_seed <= 9999):
            raise ValueError("셔플 시드는 1-9999 범위여야 합니다")


@dataclass
class ProcessingResult:
    """처리 결과를 담는 데이터 클래스"""
    
    input_file: Path
    output_directory: Path
    detection_results: List[DetectionResult]
    page_images: List[Path]
    processing_time: float
    settings: ProcessingSettings
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_questions(self) -> int:
        """감지된 총 문제 수"""
        return len(self.detection_results)
    
    @property
    def total_pages(self) -> int:
        """총 페이지 수"""
        return len(self.page_images)
    
    def get_questions_by_page(self, page_number: int) -> List[DetectionResult]:
        """특정 페이지의 문제들을 반환"""
        return [q for q in self.detection_results if q.page_number == page_number]


@dataclass
class ModelInfo:
    """모델 정보를 담는 데이터 클래스"""
    
    name: str
    path: Path
    size_mb: float
    modified_time: datetime
    model_type: str = "YOLO"
    version: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """데이터 검증"""
        if self.size_mb <= 0:
            raise ValueError("모델 크기는 0보다 커야 합니다")


@dataclass
class OutputFormat:
    """출력 형식 정보를 담는 데이터 클래스"""
    
    name: str
    enabled: bool = True
    description: str = ""
    file_extension: str = ""
    icon: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApplicationConfig:
    """애플리케이션 설정을 담는 데이터 클래스"""
    
    project_root: Path
    model_directory: Path
    output_directory: Path
    temp_directory: Path
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_workers: int = 1
    batch_size: int = 1
    
    def __post_init__(self):
        """디렉토리 생성"""
        for directory in [self.model_directory, self.output_directory, self.temp_directory]:
            directory.mkdir(parents=True, exist_ok=True) 