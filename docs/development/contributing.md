# 기여 가이드

ExamSplitter 프로젝트에 기여해주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법을 안내합니다.

## 🚀 빠른 시작 체크리스트

PR을 제출하기 전에 다음 항목들을 확인해주세요:

### ✅ 필수 체크리스트

- [ ] **커밋 메시지 규칙에 맞게 작성했나요?**
  - [Conventional Commits](https://www.conventionalcommits.org/) 형식 준수
  - 타입, 설명, 본문이 명확하게 작성됨

- [ ] **코드 스타일(isort, black) 적용했나요?**
  - `black src/` 실행으로 코드 포맷팅 완료
  - `isort src/` 실행으로 import 정렬 완료
  - 코드 스타일 검사 통과

- [ ] **타입 검사(mypy) 통과했나요?**
  - `mypy src/` 실행으로 타입 검사 통과
  - 모든 함수에 타입 어노테이션 추가
  - Optional 타입 안전성 확보

### 🔧 개발 환경 설정

**요구사항**:
- **Python**: 3.10 이상
- **OS**: Windows, macOS, Linux

```bash
# 1. 저장소 클론
git clone https://github.com/d3vksy/ExamSplitter.git
cd ExamSplitter

# 2. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 개발 도구 설치
pip install -r style.txt

# 5. 코드 품질 검사 실행
black src/
isort src/
mypy src/
```

## 기여 방법

### 이슈 리포트

버그를 발견하거나 새로운 기능을 제안하고 싶으시다면:

1. **기존 이슈 확인**: 먼저 [Issues](https://github.com/d3vksy/ExamSplitter/issues)에서 동일한 이슈가 있는지 확인
2. **새 이슈 생성**: 없다면 새 이슈를 생성하고 다음 정보를 포함:
   - **제목**: 명확하고 간결한 설명
   - **설명**: 문제 상황이나 제안 내용
   - **재현 방법**: 버그의 경우 단계별 재현 방법
   - **예상 동작**: 기대하는 결과
   - **실제 동작**: 실제 발생하는 결과
   - **환경 정보**: OS, Python 버전, 의존성 버전

### Pull Request

코드 기여를 원하신다면:

1. **Fork**: 저장소를 포크
2. **브랜치 생성**: `feature/기능명` 또는 `fix/버그명` 형식으로 브랜치 생성
3. **개발**: 코드 작성 및 테스트
4. **품질 검사**: 아래 체크리스트 완료
5. **커밋**: 명확한 커밋 메시지로 커밋
6. **Push**: 포크한 저장소에 푸시
7. **PR 생성**: 메인 저장소로 Pull Request 생성

## 개발 가이드라인

### 코드 품질 관리

#### 1. 코드 포맷팅 (Black)

**설정**: 프로젝트 루트의 `pyproject.toml`에서 Black 설정 관리

```bash
# 전체 소스 코드 포맷팅
black src/

# 특정 파일만 포맷팅
black src/ui/main_window.py

# 변경사항 미리보기 (실제 변경하지 않음)
black --check src/
```

**규칙**:
- 라인 길이: 88자
- 문자열 따옴표: 더블 쿼트
- 들여쓰기: 스페이스 4개

#### 2. Import 정렬 (isort)

```bash
# 전체 소스 코드 import 정렬
isort src/

# 특정 파일만 정렬
isort src/utils/logger.py

# 변경사항 미리보기
isort --check-only src/
```

**정렬 순서**:
1. 표준 라이브러리
2. 서드파티 라이브러리
3. 로컬 애플리케이션/라이브러리

#### 3. 타입 검사 (mypy)

**설정**: `mypy.ini` 파일에서 엄격한 타입 검사 설정

```bash
# 전체 소스 코드 타입 검사
mypy src/

# 특정 파일만 검사
mypy src/ui/main_window.py

# 에러만 표시
mypy --no-error-summary src/
```

**타입 검사 규칙**:
- 모든 함수에 반환 타입 어노테이션 필수 (`-> None`, `-> bool` 등)
- 모든 변수에 명시적 타입 어노테이션 권장
- Optional 타입 안전성 확보
- 외부 라이브러리는 타입 검사 제외

### 코드 스타일

#### Python 코드 스타일
- **PEP 8** 준수
- **Black** 포맷터 사용 
- **isort**로 import 정렬
- **mypy**로 타입 검사

#### 네이밍 컨벤션
- **클래스**: PascalCase (`MainWindow`, `QuestionDetector`)
- **함수/변수**: snake_case (`detect_questions`, `pdf_file`)
- **상수**: UPPER_SNAKE_CASE (`DEFAULT_DPI`, `SUPPORTED_FORMATS`)
- **파일명**: snake_case (`main_window.py`, `question_detector.py`)

### 커밋 메시지 규칙

[Conventional Commits](https://www.conventionalcommits.org/) 형식 사용:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 타입
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경 (기능에 영향 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스, 도구 변경

#### 예시
```
feat(ui): 문제 영역 드래그 앤 드롭 편집 기능 추가

- CanvasWidget에 마우스 이벤트 핸들러 추가
- 박스 크기 및 위치 실시간 조정 기능
- 시각적 피드백 개선

Closes #123
```

### 타입 어노테이션 가이드

#### 기본 타입 어노테이션
```python
from typing import Any, Callable, Dict, List, Optional

# 함수 타입 어노테이션
def process_pdf(self, pdf_path: str, output_dir: str) -> List[Dict]:
    pass

# 변수 타입 어노테이션
questions: List[Dict] = []
current_image: Optional[Image.Image] = None

# 매개변수 타입 어노테이션
def __init__(self, parent: Any, callback: Optional[Callable] = None) -> None:
    pass
```

#### Optional 타입 안전성
```python
# 안전하지 않은 코드
def unsafe_function(value: Optional[str]) -> None:
    print(value.upper())  # mypy 오류: value가 None일 수 있음

# 안전한 코드
def safe_function(value: Optional[str]) -> None:
    if value is not None:
        print(value.upper())
    else:
        print("값이 없습니다")
```

### 디버깅 및 문제 해결

#### 일반적인 mypy 오류 해결

1. **"Function is missing a return type annotation"**
   ```python
   # 수정 전
   def my_function():
       pass
   
   # 수정 후
   def my_function() -> None:
       pass
   ```

2. **"Incompatible types in assignment"**
   ```python
   # 수정 전
   value: Optional[str] = None
   value = "hello"  # mypy 오류
   
   # 수정 후
   value: Optional[str] = None
   value = "hello"  # 정상
   ```

3. **"Item 'None' has no attribute"**
   ```python
   # 수정 전
   if self.current_image.size:
       pass
   
   # 수정 후
   if self.current_image is not None and self.current_image.size:
       pass
   ```


## 기여자 가이드라인

### PR 리뷰 프로세스

1. **자동 검사 통과**: CI/CD 파이프라인의 모든 검사 통과
2. **코드 리뷰**: 최소 1명의 리뷰어 승인 필요
3. **테스트 통과**: 모든 테스트 케이스 통과
4. **문서 업데이트**: 관련 문서 업데이트 완료

### 기여자 행동 강령

- **존중**: 모든 기여자를 존중하고 격려
- **건설적 피드백**: 건설적이고 도움이 되는 피드백 제공
- **포용성**: 다양한 배경과 경험을 가진 기여자 환영

## 문의 및 지원

- **이슈**: [GitHub Issues](https://github.com/d3vksy/ExamSplitter/issues)

- **문서**: [프로젝트 문서](https://github.com/d3vksy/ExamSplitter/tree/main/docs)

감사합니다! 🎉







 