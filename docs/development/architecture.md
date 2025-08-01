# ExamSplitter 아키텍처 문서

## 전체 시스템 아키텍처

### 레이어 구조

**1. UI Layer (src/ui/)**
- main_window.py: 메인 애플리케이션 윈도우
- canvas_widget.py: PDF 페이지 표시 및 편집
- settings_panel.py: 사용자 설정 관리

**2. Core Layer (src/core/)**
- models.py: 데이터 모델 정의
- exceptions.py: 커스텀 예외 클래스

**3. Utils Layer (src/utils/)**
- logger.py: 로깅 시스템
- pdf_generator.py: PDF 처리 및 생성
- question_detector.py: YOLOv8 기반 문제 감지
- validators.py: 입력 데이터 검증
- model_utils.py: 모델 관련 유틸리티

**4. Configuration Layer (src/config/)**
- defaults.py: 기본 설정값
- settings.py: 설정 관리

**5. External Dependencies**
- YOLOv8 (ultralytics): 문제 영역 감지
- PyMuPDF: PDF 파일 처리
- OpenCV: 이미지 처리
- ReportLab: PDF 생성
- NumPy: 수치 계산
- Pillow: 이미지 처리

## 모듈별 역할

### 1. UI Layer (`src/ui/`)

#### `main_window.py`
- **기능**: 메인 애플리케이션 윈도우 관리
- **주요 클래스**: `MainWindow`
- **담당**:
  - 전체 UI 레이아웃 구성
  - 메뉴바 및 툴바 관리
  - 이벤트 핸들링 및 라우팅
  - 상태 관리 (로딩, 진행률 등)

#### `canvas_widget.py`
- **기능**: PDF 페이지 표시 및 상호작용
- **주요 클래스**: `CanvasWidget`
- **담당**:
  - PDF 페이지를 이미지로 렌더링
  - 드래그 앤 드롭으로 박스 편집
  - 줌 인/아웃 기능
  - 문제 영역 시각화

#### `settings_panel.py`
- **기능**: 사용자 설정 관리
- **주요 클래스**: `SettingsPanel`
- **담당**:
  - DPI, 신뢰도 등 설정 UI
  - 출력 형식 선택
  - 설정값 검증 및 저장

### 2. Core Layer (`src/core/`)

#### `models.py`
- **기능**: 데이터 모델 정의
- **주요 클래스**:
  - `QuestionBox`: 문제 영역 정보
  - `ProcessingSettings`: 처리 설정
  - `OutputFormat`: 출력 형식 열거형
- **담당**:
  - 데이터 구조 정의
  - 타입 안전성 보장

#### `exceptions.py`
- **기능**: 커스텀 예외 클래스 정의
- **주요 클래스**:
  - `ExamSplitterError`: 기본 예외 클래스
  - `PDFError`: PDF 처리 관련 오류
  - `ModelError`: 모델 로딩/실행 오류
- **담당**:
  - 명확한 오류 메시지 제공
  - 오류 타입별 처리 가능

### 3. Utils Layer (`src/utils/`)

#### `question_detector.py`
- **기능**: YOLOv8 모델을 사용한 문제 감지
- **주요 클래스**: `QuestionDetector`
- **담당**:
  - YOLOv8 모델 로딩 및 관리
  - 이미지에서 문제 영역 감지
  - 신뢰도 기반 필터링
  - 결과 후처리

#### `pdf_generator.py`
- **기능**: PDF 파일 생성 및 처리
- **주요 클래스**: `PDFGenerator`
- **담당**:
  - 원본 PDF 읽기
  - 개별 문제 PDF 생성
  - 그룹 PDF 생성
  - 전체 문제집 PDF 생성

#### `logger.py`
- **기능**: 로깅 시스템 관리
- **주요 클래스**: `Logger`
- **담당**:
  - 로그 레벨 관리
  - 파일 및 콘솔 출력
  - 로그 포맷팅
  - 로그 로테이션

#### `validators.py`
- **기능**: 입력 데이터 검증
- **주요 함수**:
  - `validate_pdf_file()`: PDF 파일 검증
  - `validate_settings()`: 설정값 검증
  - `validate_output_path()`: 출력 경로 검증
- **담당**:
  - 데이터 무결성 보장
  - 사용자 입력 검증

#### `model_utils.py`
- **기능**: 모델 관련 유틸리티 함수
- **주요 함수**:
  - `get_model_directory()`: 모델 디렉토리 경로 반환
  - `get_model_path()`: 모델 파일 경로 반환
  - `get_available_models()`: 사용 가능한 모델 목록 반환
  - `get_model_info()`: 모델 정보 반환
- **담당**:
  - 모델 파일 경로 관리
  - 개발/배포 환경 호환성
  - 모델 메타데이터 제공

### 4. Configuration Layer (`src/config/`)

#### `settings.py`
- **기능**: 애플리케이션 설정 관리
- **주요 클래스**: `Settings`
- **담당**:
  - 설정 파일 읽기/쓰기
  - 기본값 관리
  - 설정 변경 감지

#### `defaults.py`
- **기능**: 기본 설정값 정의
- **주요 상수**:
  - `DEFAULT_DPI`: 기본 DPI 값
  - `DEFAULT_CONFIDENCE`: 기본 신뢰도
  - `SUPPORTED_FORMATS`: 지원되는 출력 형식
- **담당**:
  - 일관된 기본값 제공
  - 설정 상수 중앙 관리

## 데이터 흐름

### 1. PDF 업로드 및 처리
1. 사용자가 PDF 파일 선택
2. PDFGenerator.read_pdf() 함수로 PDF 읽기
3. CanvasWidget.display_page()로 페이지 표시

### 2. 문제 감지
1. PDF 페이지를 이미지로 변환
2. QuestionDetector.detect() 함수로 YOLOv8 모델 실행
3. 감지된 영역을 QuestionBox 객체로 변환
4. CanvasWidget.draw_boxes()로 시각화

### 3. 사용자 편집
1. 사용자가 마우스로 박스 드래그/조정
2. CanvasWidget.handle_mouse() 이벤트 핸들러 실행
3. QuestionBox 객체 업데이트
4. UI 자동 갱신

### 4. 출력 생성
1. QuestionBox 리스트와 사용자 설정 수집
2. PDFGenerator.generate() 함수로 출력 파일 생성
3. 선택된 형식(개별 PDF, 그룹 PDF 등)으로 저장

 