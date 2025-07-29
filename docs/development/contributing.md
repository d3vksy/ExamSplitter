# 기여 가이드

ExamSplitter 프로젝트에 기여해주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법을 안내합니다.

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
4. **커밋**: 명확한 커밋 메시지로 커밋
5. **Push**: 포크한 저장소에 푸시
6. **PR 생성**: 메인 저장소로 Pull Request 생성

## 개발 가이드라인

### 코드 스타일

#### Python 코드 스타일
- **PEP 8** 준수
- **Black** 포맷터 사용 (라인 길이 88자)
- **isort**로 import 정렬
- **flake8**로 린팅

#### 설정 방법
```bash
# 개발 의존성 설치
pip install black isort flake8

# 코드 포맷팅
black src/
isort src/

# 린팅
flake8 src/
```

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







 