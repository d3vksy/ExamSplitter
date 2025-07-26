# ExamSplitter 배포 가이드

ExamSplitter는 GitHub Actions를 사용한 자동 배포 시스템을 구축했습니다.

### 배포 워크플로우

#### 1. Beta 테스트 (BETA 브랜치)
```bash
# BETA 브랜치에서 테스트 빌드
git checkout BETA
git commit -m "deploy(1.0.0): beta 테스트 빌드"
git push origin BETA
```

**결과:**
- PyInstaller 빌드 테스트
- Artifacts에 실행 파일 업로드
- 커밋에 테스트 결과 댓글
- GitHub Releases에는 업로드 안됨

#### 2. 최종 배포 (main 브랜치)
```bash
# main 브랜치로 머지 후 배포
git checkout main
git merge BETA
git commit -m "deploy(1.0.0): 최종 버전 배포"
git push origin main
```

**결과:**
- PyInstaller 빌드
- GitHub Releases에 자동 업로드
- 태그 생성
- 릴리즈 노트 자동 생성

#### 3. GitHub Actions 수동 실행
1. GitHub 저장소 → Actions 탭
2. "Deploy ExamSplitter" 워크플로우 선택
3. "Run workflow" 클릭
4. 버전 입력 후 실행

### 배포 과정

1. **Beta 테스트**: BETA 브랜치에서 `deploy(버전명)` 커밋
2. **테스트 확인**: 다운로드한 실행 파일 테스트
3. **Main 머지**: 문제 없으면 main 브랜치로 머지
4. **최종 배포**: main에서 `deploy(버전명)` 커밋으로 배포

### 배포 결과물

- **Beta**: `ExamSplitter-Beta-v{버전}.zip` (Artifacts)
- **Main**: `ExamSplitter-v{버전}.zip` (GitHub Releases)
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

