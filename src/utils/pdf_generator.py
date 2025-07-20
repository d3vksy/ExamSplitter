"""
PDF 생성 모듈
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

class PDFGenerator:
    """PDF 생성 클래스"""
    
    def __init__(self):
        self.initialized = False
    
    def create_individual_pdfs(self, question_images: List[str], output_dir: str) -> List[str]:
        """개별 PDF 파일들을 생성합니다."""
        created_files = []
        
        for i, img_path in enumerate(question_images):
            try:
                # 이미지 파일 존재 확인
                if not Path(img_path).exists():
                    continue
                
                output_path = os.path.join(output_dir, f"문제_{i+1:03d}.pdf")
                self._create_single_pdf(img_path, output_path)
                created_files.append(output_path)
            except Exception as e:
                pass
        
        return created_files
    
    def group_questions(self, question_images: List[str], group_size: int) -> List[List[str]]:
        """문제들을 그룹으로 나눕니다."""
        groups = []
        for i in range(0, len(question_images), group_size):
            group = question_images[i:i + group_size]
            groups.append(group)
        return groups
    
    def create_grouped_pdfs(self, groups: List[List[str]], output_dir: str) -> List[str]:
        """그룹 PDF 파일들을 생성합니다."""
        created_files = []
        
        for i, group in enumerate(groups):
            try:
                output_path = os.path.join(output_dir, f"그룹_{i+1:03d}.pdf")
                self._create_group_pdf(group, output_path)
                created_files.append(output_path)
            except Exception as e:
                pass
        
        return created_files
    
    def create_exam_workbook(self, questions: List[Dict], metadata: Dict, output_path: str) -> None:
        """전체 문제집 PDF를 생성합니다."""
        try:
            question_images = [q['image_path'] for q in questions]
            self._create_group_pdf(question_images, output_path)
        except Exception as e:
            raise Exception(f"전체 문제집 생성 실패: {e}")
    
    def create_shuffled_workbook(self, questions: List[Dict], metadata: Dict, 
                                output_path: str, seed: Optional[int] = None) -> None:
        """셔플된 문제집 PDF를 생성합니다."""
        try:
            import random
            
            if seed is not None:
                random.seed(seed)
            
            question_images = [q['image_path'] for q in questions]
            shuffled_images = question_images.copy()
            random.shuffle(shuffled_images)
            
            self._create_group_pdf(shuffled_images, output_path)
        except Exception as e:
            raise Exception(f"셔플 문제집 생성 실패: {e}")
    
    def _create_single_pdf(self, image_path: str, output_path: str) -> None:
        """단일 이미지를 PDF로 변환합니다."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # PDF 생성
            c = canvas.Canvas(output_path, pagesize=(img_width, img_height))
            c.drawImage(image_path, 0, 0, img_width, img_height)
            c.save()
            
        except Exception as e:
            raise Exception(f"단일 PDF 생성 실패: {e}")
    
    def _create_group_pdf(self, image_paths: List[str], output_path: str) -> None:
        """여러 이미지를 하나의 PDF로 결합합니다."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(output_path)
            
            for img_path in image_paths:
                img = Image.open(img_path)
                img_width, img_height = img.size
                
                # 페이지 크기 설정
                c.setPageSize((img_width, img_height))
                c.drawImage(img_path, 0, 0, img_width, img_height)
                c.showPage()
            
            c.save()
            
        except Exception as e:
            raise Exception(f"그룹 PDF 생성 실패: {e}")
    
    def cleanup(self):
        """리소스 정리 작업을 수행합니다."""
        try:
            # 초기화 상태 리셋
            self.initialized = False
            
        except Exception as e:
            # 정리 작업 중 오류가 발생해도 무시
            pass 