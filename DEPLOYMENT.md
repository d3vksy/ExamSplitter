# ExamSplitter 배포 가이드

ExamSplitter는 GitHub Actions를 사용한 자동 배포 시스템을 구축했습니다.

### 배포 방법

#### 1. 커밋 메시지로 자동 배포
```bash
# 버전 1.0.0 배포
git commit -m "deploy(1.0.0): 초기 버전 배포"

# 버전 1.1.0 배포  
git commit -m "deploy(1.1.0): UI 개선 및 버그 수정"

# 버전 2.0.0 배포
git commit -m "deploy(2.0.0): 새로운 기능 추가"
```

#### 2. GitHub Actions 수동 실행
1. GitHub 저장소 → Actions 탭
2. "Deploy ExamSplitter" 워크플로우 선택
3. "Run workflow" 클릭
4. 버전 입력 후 실행

### 배포 과정

1. **트리거**: `deploy(버전명)` 패턴의 커밋 메시지로 push
2. **빌드**: Windows 환경에서 PyInstaller로 실행 파일 생성
3. **패키징**: 실행 파일, README, LICENSE, models 폴더를 ZIP으로 압축
4. **릴리즈**: GitHub Releases에 자동 업로드

### 배포 결과물

- `ExamSplitter-v{버전}.zip`: Windows 실행 파일 패키지
- GitHub Releases에 자동 태그 생성
- 릴리즈 노트 자동 생성

## 로컬 빌드

### 1. 빌드 스크립트 사용
```bash
python build.py
```

### 2. 수동 PyInstaller 빌드
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ExamSplitter \
  --add-data "models;models" \
  --add-data "banner.png;." \
  --icon "banner.png" \
  --hidden-import ultralytics \
  --hidden-import cv2 \
  --hidden-import fitz \
  --hidden-import PIL \
  --hidden-import reportlab \
  --hidden-import numpy \
  --hidden-import tkinter \
  --clean \
  main.py
```

## 테스트 빌드

Pull Request가 생성되면 자동으로 테스트 빌드가 실행됩니다:

1. **빌드 테스트**: PyInstaller로 실행 파일 생성 테스트
2. **검증**: 실행 파일 존재 및 크기 확인
3. **아티팩트**: 빌드 결과물을 GitHub Actions 아티팩트로 저장


## 설정 및 커스터마이징

### 워크플로우 수정
`.github/workflows/deploy.yml` 파일을 수정하여 배포 과정을 커스터마이징할 수 있습니다:

- **Python 버전**: `python-version: '3.9'` 변경
- **PyInstaller 옵션**: `--hidden-import` 추가/제거
- **릴리즈 노트**: `body:` 섹션 수정
