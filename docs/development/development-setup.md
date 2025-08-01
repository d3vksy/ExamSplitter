# 개발 환경 설정 가이드

## 필수 요구사항

- Python 3.10 이상
- Git

## 1. 저장소 클론

```bash
git clone https://github.com/d3vksy/ExamSplitter.git
cd ExamSplitter
```

## 2. 가상환경 설정

### 가상환경 생성
```bash
python -m venv .venv
```

### 가상환경 활성화
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

## 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 주요 의존성
- `opencv-python`: 이미지 처리 및 컴퓨터 비전
- `PyMuPDF`: PDF 파일 읽기/쓰기
- `ultralytics`: YOLOv8 모델 실행
- `numpy`: 수치 계산
- `Pillow`: 이미지 처리
- `reportlab`: PDF 생성
- `pyinstaller`: 실행 파일 빌드



## 4. 로컬 실행

```bash
python main.py
```

## 5. 로컬 빌드 테스트

```bash
python build_pyinstaller.py
```

빌드 결과물: `dist/ExamSplitter/ExamSplitter.exe`

## 6. 개발 시 주의사항

- `models/` 폴더에 YOLOv8 모델 파일들 (.pt)이 있어야 함
- `logs/` 폴더에 로그 파일 생성됨
- `temp/` 폴더에 임시 파일들이 생성됨
