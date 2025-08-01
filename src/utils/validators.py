"""
입력 검증 유틸리티 모듈
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from .logger import get_logger

logger = get_logger(__name__)


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """파일 경로의 유효성을 검사합니다.

    Args:
        file_path: 검사할 파일 경로

    Returns:
        검증된 Path 객체

    Raises:
        ValueError: 파일 경로가 유효하지 않은 경우
        FileNotFoundError: 파일이 존재하지 않는 경우
    """
    if not file_path:
        raise ValueError("파일 경로가 비어있습니다")

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    if not path.is_file():
        raise ValueError(f"경로가 파일이 아닙니다: {path}")

    return path


def validate_directory_path(directory_path: Union[str, Path]) -> Path:
    """디렉토리 경로의 유효성을 검사합니다.

    Args:
        directory_path: 검사할 디렉토리 경로

    Returns:
        검증된 Path 객체

    Raises:
        ValueError: 디렉토리 경로가 유효하지 않은 경우
        FileNotFoundError: 디렉토리가 존재하지 않는 경우
    """
    if not directory_path:
        raise ValueError("디렉토리 경로가 비어있습니다")

    path = Path(directory_path)

    if not path.exists():
        raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {path}")

    if not path.is_dir():
        raise ValueError(f"경로가 디렉토리가 아닙니다: {path}")

    return path


def validate_pdf_file(file_path: Union[str, Path]) -> Path:
    """PDF 파일의 유효성을 검사합니다.

    Args:
        file_path: 검사할 PDF 파일 경로

    Returns:
        검증된 Path 객체

    Raises:
        ValueError: PDF 파일이 유효하지 않은 경우
    """
    path = validate_file_path(file_path)

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"PDF 파일이 아닙니다: {path}")

        # 파일 크기 검사
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 50:
        raise ValueError(f"파일 크기가 너무 큽니다: {file_size_mb:.1f}MB (최대 50MB)")

    return path


def validate_image_file(file_path: Union[str, Path]) -> Path:
    """이미지 파일의 유효성을 검사합니다.

    Args:
        file_path: 검사할 이미지 파일 경로

    Returns:
        검증된 Path 객체

    Raises:
        ValueError: 이미지 파일이 유효하지 않은 경우
    """
    path = validate_file_path(file_path)

    valid_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"지원하지 않는 이미지 형식입니다: {path.suffix}")

    return path


def validate_dpi(dpi: int) -> int:
    """DPI 값의 유효성을 검사합니다.

    Args:
        dpi: 검사할 DPI 값

    Returns:
        검증된 DPI 값

    Raises:
        ValueError: DPI 값이 유효하지 않은 경우
    """
    if not isinstance(dpi, int):
        raise ValueError("DPI는 정수여야 합니다")

    if dpi < 150 or dpi > 600:
        raise ValueError(f"DPI는 150-600 범위여야 합니다: {dpi}")

    return dpi


def validate_confidence(confidence: float) -> float:
    """신뢰도 값의 유효성을 검사합니다.

    Args:
        confidence: 검사할 신뢰도 값

    Returns:
        검증된 신뢰도 값

    Raises:
        ValueError: 신뢰도 값이 유효하지 않은 경우
    """
    if not isinstance(confidence, (int, float)):
        raise ValueError("신뢰도는 숫자여야 합니다")

    if confidence < 0.1 or confidence > 1.0:
        raise ValueError(f"신뢰도는 0.1-1.0 범위여야 합니다: {confidence}")

    return float(confidence)


def validate_group_size(group_size: int) -> int:
    """그룹 크기 값의 유효성을 검사합니다.

    Args:
        group_size: 검사할 그룹 크기 값

    Returns:
        검증된 그룹 크기 값

    Raises:
        ValueError: 그룹 크기 값이 유효하지 않은 경우
    """
    if not isinstance(group_size, int):
        raise ValueError("그룹 크기는 정수여야 합니다")

    if group_size < 1 or group_size > 20:
        raise ValueError(f"그룹 크기는 1-20 범위여야 합니다: {group_size}")

    return group_size


def validate_shuffle_seed(seed: Optional[int]) -> Optional[int]:
    """셔플 시드 값의 유효성을 검사합니다.

    Args:
        seed: 검사할 셔플 시드 값

    Returns:
        검증된 셔플 시드 값

    Raises:
        ValueError: 셔플 시드 값이 유효하지 않은 경우
    """
    if seed is None:
        return None

    if not isinstance(seed, int):
        raise ValueError("셔플 시드는 정수여야 합니다")

    if seed < 1 or seed > 9999:
        raise ValueError(f"셔플 시드는 1-9999 범위여야 합니다: {seed}")

    return seed


def validate_output_formats(output_formats: dict) -> dict:
    """출력 형식 설정의 유효성을 검사합니다.

    Args:
        output_formats: 검사할 출력 형식 설정

    Returns:
        검증된 출력 형식 설정

    Raises:
        ValueError: 출력 형식 설정이 유효하지 않은 경우
    """
    if not isinstance(output_formats, dict):
        raise ValueError("출력 형식은 딕셔너리여야 합니다")

    valid_formats = [
        "개별 이미지",
        "개별 PDF",
        "그룹 PDF",
        "전체 문제집",
        "셔플 문제집",
    ]

    validated_formats = {}
    for format_name, enabled in output_formats.items():
        if format_name not in valid_formats:
            logger.warning(f"알 수 없는 출력 형식: {format_name}")
            continue

        if not isinstance(enabled, bool):
            raise ValueError(f"출력 형식 활성화 값은 불린이어야 합니다: {format_name}")

        validated_formats[format_name] = enabled

    return validated_formats


def validate_model_path(model_path: Optional[Union[str, Path]]) -> Optional[Path]:
    """모델 파일 경로의 유효성을 검사합니다.

    Args:
        model_path: 검사할 모델 파일 경로

    Returns:
        검증된 Path 객체 또는 None

    Raises:
        ValueError: 모델 파일 경로가 유효하지 않은 경우
    """
    if model_path is None:
        return None

    path = validate_file_path(model_path)

    valid_extensions = [".pt", ".pth", ".onnx", ".engine"]
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"지원하지 않는 모델 형식입니다: {path.suffix}")

    return path


def validate_bounding_box(bounding_box: List[float]) -> List[float]:
    """바운딩 박스 값의 유효성을 검사합니다.

    Args:
        bounding_box: 검사할 바운딩 박스 [x1, y1, x2, y2]

    Returns:
        검증된 바운딩 박스

    Raises:
        ValueError: 바운딩 박스 값이 유효하지 않은 경우
    """
    if not isinstance(bounding_box, list):
        raise ValueError("바운딩 박스는 리스트여야 합니다")

    if len(bounding_box) != 4:
        raise ValueError(f"바운딩 박스는 4개의 값이 필요합니다: {len(bounding_box)}개")

    for i, value in enumerate(bounding_box):
        if not isinstance(value, (int, float)):
            raise ValueError(f"바운딩 박스 값 {i}는 숫자여야 합니다: {value}")
        if value < 0:
            raise ValueError(f"바운딩 박스 값 {i}는 음수일 수 없습니다: {value}")

    x1, y1, x2, y2 = bounding_box
    if x2 <= x1 or y2 <= y1:
        raise ValueError("바운딩 박스의 크기가 유효하지 않습니다")

    return [float(x) for x in bounding_box]


def validate_file_permissions(
    file_path: Union[str, Path], check_write: bool = False
) -> bool:
    """파일 권한을 검사합니다.

    Args:
        file_path: 검사할 파일 경로
        check_write: 쓰기 권한도 검사할지 여부

    Returns:
        권한 검사 결과

    Raises:
        PermissionError: 권한이 없는 경우
    """
    path = Path(file_path)

    if not path.exists():
        return True  # 존재하지 않는 파일은 권한 검사 불필요

    if not os.access(path, os.R_OK):
        raise PermissionError(f"파일 읽기 권한이 없습니다: {path}")

    if check_write and not os.access(path, os.W_OK):
        raise PermissionError(f"파일 쓰기 권한이 없습니다: {path}")

    return True


def validate_directory_permissions(directory_path: Union[str, Path]) -> bool:
    """디렉토리 권한을 검사합니다.

    Args:
        directory_path: 검사할 디렉토리 경로

    Returns:
        권한 검사 결과

    Raises:
        PermissionError: 권한이 없는 경우
    """
    path = Path(directory_path)

    if not path.exists():
        # 디렉토리가 없으면 상위 디렉토리 권한 검사
        parent = path.parent
        if parent.exists() and not os.access(parent, os.W_OK):
            raise PermissionError(f"디렉토리 생성 권한이 없습니다: {parent}")
        return True

    if not os.access(path, os.R_OK):
        raise PermissionError(f"디렉토리 읽기 권한이 없습니다: {path}")

    if not os.access(path, os.W_OK):
        raise PermissionError(f"디렉토리 쓰기 권한이 없습니다: {path}")

    return True
