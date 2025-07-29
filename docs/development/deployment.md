# 배포 가이드

ExamSplitter의 배포 프로세스와 GitHub Actions 워크플로우에 대한 상세 가이드입니다.

## 배포 시스템 개요

ExamSplitter는 GitHub Actions를 사용한 자동화된 배포 시스템을 구축했습니다:

- **Beta 테스트**: BETA 브랜치에서 테스트 빌드
- **최종 배포**: main 브랜치에서 정식 릴리즈
- **자동화**: PyInstaller 빌드, 패키징, GitHub Releases 업로드

## 워크플로우 구조

### 1. Beta 테스트 워크플로우 (`.github/workflows/beta-test.yml`)

**트리거**: BETA 브랜치에 push
**목적**: 테스트 빌드 및 검증

#### 주요 단계:
1. **환경 설정**: Python 3.9, 의존성 설치
2. **빌드**: PyInstaller로 실행 파일 생성
3. **검증**: 실행 파일 존재 및 크기 확인
4. **패키징**: ZIP 파일 생성
5. **아티팩트 업로드**: GitHub Actions 아티팩트로 저장

#### 결과물:
- `ExamSplitter-Beta.zip` (아티팩트)
- 빌드 요약 (GitHub Actions UI)

### 2. 최종 배포 워크플로우 (`.github/workflows/deploy.yml`)

**트리거**: 
- main 브랜치에 push (deploy 패턴 포함)
- 수동 워크플로우 실행

**목적**: 정식 릴리즈 배포

#### 주요 단계:
1. **환경 설정**: Python 3.9, 의존성 설치
2. **버전 추출**: 커밋 메시지에서 버전 파싱
3. **빌드**: PyInstaller로 실행 파일 생성
4. **패키징**: 버전별 ZIP 파일 생성
5. **릴리즈 생성**: GitHub Releases에 자동 업로드

#### 결과물:
- `ExamSplitter-v{버전}.zip` (GitHub Releases)
- 자동 태그 생성
- 릴리즈 노트 자동 생성

## 배포 프로세스

### 1. Beta 테스트 배포

```bash
# BETA 브랜치로 전환
git checkout BETA

# 변경사항 커밋
git add .
git commit -m "feat: 새로운 기능 추가"

# BETA 브랜치에 푸시 (자동으로 테스트 빌드 실행)
git push origin BETA
```

**확인 방법:**
1. GitHub 저장소 → Actions 탭
2. "Beta Test Build" 워크플로우 확인
3. 아티팩트에서 `ExamSplitter-Beta.zip` 다운로드
4. 로컬에서 테스트 실행

### 2. 최종 배포

```bash
# main 브랜치로 전환
git checkout main

# BETA 브랜치 머지
git merge BETA

# 배포 커밋 (버전 포함)
git commit -m "deploy(1.2.0): 최종 버전 배포"

# main 브랜치에 푸시 (자동으로 릴리즈 생성)
git push origin main
```

**확인 방법:**
1. GitHub 저장소 → Releases 탭
2. 새 릴리즈 확인
3. `ExamSplitter-v1.2.0.zip` 다운로드

### 3. 수동 배포

GitHub Actions UI에서 수동으로 배포할 수 있습니다:

1. GitHub 저장소 → Actions 탭
2. "Deploy ExamSplitter" 워크플로우 선택
3. "Run workflow" 클릭
4. 버전 입력 (예: `1.2.0`)
5. 실행

## 빌드 스크립트 상세

### PyInstaller 설정 (`build_pyinstaller.py`)

```python
# 주요 PyInstaller 옵션
cmd = [
    "pyinstaller",
    ENTRY_FILE,
    "--onedir",           # 단일 폴더로 빌드
    "--noconsole",        # 콘솔 창 숨김
    "--clean",            # 캐시 정리
    f"--name={PROJECT_NAME}",
    "--hidden-import=ultralytics",  # YOLOv8
    "--hidden-import=torch",        # PyTorch
    "--hidden-import=cv2",          # OpenCV
    "--hidden-import=fitz",         # PyMuPDF
    "--hidden-import=pymupdf",      # PyMuPDF (별칭)
    f'--add-data="{banner_abs};."', # 배너 이미지 포함
    "--distpath=dist",              # 출력 디렉토리
    "--workpath=build",             # 작업 디렉토리
    "--log-level=INFO"              # 로그 레벨
]
```

### 모델 파일 복사

빌드 후 `models/` 폴더를 실행 파일과 함께 복사:

```python
def copy_models_to_dist():
    source_model_dir = Path(MODEL_DIR)
    target_model_dir = Path(f"dist/{PROJECT_NAME}/{MODEL_DIR}")
    
    if target_model_dir.exists():
        shutil.rmtree(target_model_dir)
    shutil.copytree(source_model_dir, target_model_dir)
```

## 문제 해결

### 1. 빌드 실패

**증상**: PyInstaller 빌드 중 오류 발생
**해결 방법**:
```bash
# 캐시 정리
rmdir /s build dist
python build_pyinstaller.py
```

**일반적인 원인**:
- 의존성 누락: `--hidden-import` 추가
- 파일 경로 문제: 절대 경로 사용
- 권한 문제: 관리자 권한으로 실행

### 2. 실행 파일 크기 문제

**증상**: 실행 파일이 너무 큼
**해결 방법**:
```bash
# UPX 압축 사용 (선택사항)
pip install upx
python build_pyinstaller.py --upx
```

### 3. 런타임 오류

**증상**: 빌드는 성공했지만 실행 시 ImportError
**해결 방법**:
- 누락된 의존성 확인
- `--hidden-import` 옵션 추가
- 모델 파일 경로 확인

### 4. GitHub Actions 오류

**증상**: 워크플로우 실행 실패
**해결 방법**:
1. Actions 로그 확인
2. Python 버전 호환성 확인
3. 의존성 버전 충돌 확인
4. 권한 문제 확인 (GITHUB_TOKEN)

 