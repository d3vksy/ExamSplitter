"""
문제 감지 모듈
"""

import os
import cv2
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional

class QuestionDetector:
    """문제 감지 클래스"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model = None
        self.initialized = False
        self.model_path = None
        
        # 초기화 시 모델 자동 로드
        if model_name:
            self._load_model(self._get_model_path(model_name))
        else:
            self._load_model()
    
    def change_model(self, model_name: str) -> bool:
        """모델을 변경합니다.
        
        Args:
            model_name: 모델 파일명 (예: "best.pt", "model2.pt")
            
        Returns:
            bool: 모델 변경 성공 여부
        """
        try:
            # 모델 경로 설정
            model_path = self._get_model_path(model_name)
            
            if not model_path.exists():
                return False
            
            # 기존 모델 해제
            if self.model is not None:
                del self.model
                self.model = None
            
            # 초기화 상태 리셋
            self.initialized = False
            self.model_path = None
            
            # 새 모델 로드
            self._load_model(str(model_path))
            
            if self.initialized:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def _get_model_path(self, model_name: str) -> Path:
        """모델 파일의 경로를 반환합니다. exe 파일과 개발 환경 모두 지원합니다."""
        try:
            # 1. 현재 작업 디렉토리 기준으로 models 폴더 찾기
            current_dir = Path.cwd()
            model_path = current_dir / "models" / model_name
            
            if model_path.exists():
                return model_path
            
            # 2. 스크립트 파일 기준으로 상대 경로 찾기 (개발 환경)
            script_dir = Path(__file__).parent.parent.parent
            model_path = script_dir / "models" / model_name
            
            if model_path.exists():
                return model_path
            
            # 3. exe 파일 기준으로 상대 경로 찾기
            import sys
            if getattr(sys, 'frozen', False):
                # exe 파일로 실행된 경우
                exe_dir = Path(sys.executable).parent
                model_path = exe_dir / "models" / model_name
                
                if model_path.exists():
                    return model_path
                
                # exe 파일과 같은 디렉토리에 models 폴더가 있는 경우
                model_path = exe_dir / "models" / model_name
                if model_path.exists():
                    return model_path
            
            # 4. 환경 변수나 다른 방법으로 찾기
            import os
            for search_path in os.environ.get('MODEL_PATH', '').split(os.pathsep):
                if search_path:
                    model_path = Path(search_path) / model_name
                    if model_path.exists():
                        return model_path
            
            # 찾지 못한 경우 기본 경로 반환
            return Path.cwd() / "models" / model_name
            
        except Exception as e:
            # 오류 발생 시 기본 경로 반환
            return Path.cwd() / "models" / model_name
    
    def _load_model(self, model_path: Optional[str] = None) -> None:
        """YOLO 모델을 로드합니다."""
        try:
            from ultralytics import YOLO
            
            if model_path is None:
                # 기본 모델 경로 설정 - models 폴더에서 첫 번째 .pt 파일 찾기
                models_dir = Path.cwd() / "models"
                
                # exe 파일인 경우 exe 디렉토리에서 찾기
                import sys
                if getattr(sys, 'frozen', False):
                    exe_dir = Path(sys.executable).parent
                    models_dir = exe_dir / "models"
                
                if models_dir.exists():
                    pt_files = list(models_dir.glob("*.pt"))
                    if pt_files:
                        model_path = str(pt_files[0])  # 첫 번째 .pt 파일 사용
                    else:
                        raise FileNotFoundError(f"models 폴더에 .pt 파일이 없습니다: {models_dir}")
                else:
                    raise FileNotFoundError(f"models 폴더를 찾을 수 없습니다: {models_dir}")
            
            if not Path(model_path).exists():
                raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")
            
            self.model = YOLO(str(model_path))
            self.model_path = str(model_path)
            self.initialized = True
            
        except ImportError as e:
            self.initialized = False
            raise ImportError("ultralytics 라이브러리가 설치되지 않았습니다. 'pip install ultralytics'를 실행하세요.")
        except FileNotFoundError as e:
            self.initialized = False
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {str(e)}")
        except Exception as e:
            self.initialized = False
            raise Exception(f"모델 로드 중 오류 발생: {str(e)}")
    
    def process_pdf(self, pdf_path: str, output_dir: str, dpi: int, confidence: float, 
                   progress_callback: Optional[Callable] = None) -> tuple[List[Dict], List[str]]:
        """PDF를 처리하여 문제를 감지합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            output_dir: 출력 디렉토리
            dpi: 이미지 DPI
            confidence: 감지 신뢰도
            progress_callback: 진행률 콜백 함수
            
        Returns:
            (questions, page_images): 감지된 문제 목록과 페이지 이미지 경로 목록
        """
        try:
            if progress_callback:
                progress_callback(10, "모델을 로드 중입니다...")
            
            # 모델 로드
            if not self.initialized:
                try:
                    self._load_model()
                except Exception as e:
                    raise Exception(f"모델 로드 실패: {str(e)}")
            
            if progress_callback:
                progress_callback(20, "PDF 파일을 분석 중입니다...")
            
            questions = []
            page_images = []
            
            # PDF를 이미지로 변환
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                if progress_callback:
                    progress = 20 + (page_num * 60 // total_pages)
                    progress_callback(progress, f"페이지 {page_num + 1}/{total_pages} 처리 중...")
                
                page = doc.load_page(page_num)
                mat = fitz.Matrix(dpi/72, dpi/72)  # DPI 변환
                pix = page.get_pixmap(matrix=mat)
                
                # 이미지 저장
                img_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                pix.save(img_path)
                page_images.append(img_path)
                
                # 문제 감지
                page_questions = self._detect_questions_on_page(img_path, page_num + 1, confidence)
                questions.extend(page_questions)
            
            doc.close()
            
            if progress_callback:
                progress_callback(90, "결과를 정리 중입니다...")
            
            # 개별 문제 이미지 생성
            questions = self._create_individual_question_images(questions, output_dir)
            
            def sort_key(q):
                x1, y1, x2, y2 = q['box']
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                if center_x < 0.5:
                    return (q['page'], 0, center_y)
                else:
                    return (q['page'], 1, center_y)
            
            questions.sort(key=sort_key)
            
            if progress_callback:
                progress_callback(100, f"문제 감지 완료: {len(questions)}개 문제 발견")
            
            return questions, page_images
            
        except Exception as e:
            raise Exception(f"PDF 처리 중 오류 발생: {str(e)}")
    
    def _detect_questions_on_page(self, image_path: str, page_num: int, confidence: float) -> List[Dict]:
        """페이지에서 문제를 감지합니다."""
        questions = []
        
        try:
            if self.initialized and self.model:
                # YOLO 모델로 감지
                results = self.model(image_path, conf=confidence, verbose=False)
                
                for i, result in enumerate(results):
                    boxes = result.boxes
                    if boxes is not None:
                        for j, box in enumerate(boxes):
                            # 바운딩 박스 좌표 (정규화된 좌표)
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = float(box.conf[0].cpu().numpy())
                            
                            # 이미지 크기로 정규화
                            img = cv2.imread(image_path)
                            if img is not None:
                                h, w = img.shape[:2]
                                x1_norm, y1_norm = x1 / w, y1 / h
                                x2_norm, y2_norm = x2 / w, y2 / h
                                
                                questions.append({
                                    'id': f"page_{page_num}_q_{len(questions)+1}",
                                    'page': page_num,
                                    'box': [x1_norm, y1_norm, x2_norm, y2_norm],
                                    'confidence': conf,
                                    'image_path': image_path
                                })
                
            else:
                # 모델이 없거나 로드 실패 시 예외 발생
                raise Exception("모델이 로드되지 않았습니다. models 폴더에 .pt 파일이 있는지 확인하세요.")
                
        except Exception as e:
            # 오류 발생 시 예외를 다시 발생시킴
            raise Exception(f"문제 감지 중 오류 발생: {str(e)}")
        
        return questions
    
    def _create_individual_question_images(self, questions: List[Dict], output_dir: str) -> List[Dict]:
        """개별 문제 이미지를 생성합니다."""
        
        for i, question in enumerate(questions):
            try:
                # 원본 이미지 로드
                img = cv2.imread(question['image_path'])
                if img is None:
                    continue
                
                h, w = img.shape[:2]
                
                # 정규화된 좌표를 픽셀 좌표로 변환
                x1 = int(question['box'][0] * w)
                y1 = int(question['box'][1] * h)
                x2 = int(question['box'][2] * w)
                y2 = int(question['box'][3] * h)
                
                # 경계 확인
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                
                # 문제 영역 추출
                question_img = img[y1:y2, x1:x2]
                
                # 개별 이미지 저장
                question_img_path = os.path.join(output_dir, f"question_{question['page']}_{i+1}.png")
                cv2.imwrite(question_img_path, question_img)
                
                # 질문 정보 업데이트
                question['image_path'] = question_img_path
                
            except Exception as e:
                # 실패 시 원본 이미지 경로 유지
                pass
        
        return questions
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보를 반환합니다."""
        if self.model_path and Path(self.model_path).exists():
            size_mb = Path(self.model_path).stat().st_size / (1024 * 1024)
            return {
                'name': Path(self.model_path).name,
                'size_mb': f"{size_mb:.1f}",
                'path': self.model_path,
                'loaded': self.initialized
            }
        else:
            return {
                'name': '모델 없음',
                'size_mb': '0.0',
                'path': '',
                'loaded': False
            }
    
    def cleanup(self):
        """리소스 정리 작업을 수행합니다."""
        try:
            # 모델 해제
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
            
            # 초기화 상태 리셋
            self.initialized = False
            self.model_path = None
            
        except Exception as e:
            # 정리 작업 중 오류가 발생해도 무시
            pass 