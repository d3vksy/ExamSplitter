#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인 윈도우 클래스
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading
import cv2
from PIL import Image, ImageTk

from .canvas_widget import ImageCanvas
from .settings_panel import SettingsPanel
from ..utils.question_detector import QuestionDetector
from ..utils.pdf_generator import PDFGenerator
from ..config.settings import get_processing_settings

class MainWindow:
    def __init__(self, root, config=None):
        self.root = root
        self.config = config
        self.root.title("ExamSplitter - PDF 시험지 문제 분할 도구")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = min(max(int(screen_width * 0.8), 800), 1400)
        window_height = min(max(int(screen_height * 0.8), 600), 1000)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        self.current_pdf_path = None
        self.questions = []
        self.page_images = []
        self.temp_output = ""
        self.processed = False
        
        self.detector = None
        self.pdf_generator = None
        
        self.setup_ui()
        self.setup_menu()
        self.update_ui_state()
        self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        top_frame = ttk.Frame(main_frame, height=40)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        top_frame.pack_propagate(False)
        
        self.upload_btn = ttk.Button(top_frame, text="PDF 파일 선택", command=self.select_pdf_file)
        self.upload_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        settings_container = ttk.Frame(center_frame)
        settings_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.settings_panel = SettingsPanel(settings_container, self.on_settings_changed, self.detector)
        self.settings_panel.pack(fill=tk.BOTH, expand=True)
        
        canvas_frame = ttk.Frame(center_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        canvas_title_frame = ttk.Frame(canvas_frame, height=25)
        canvas_title_frame.pack(fill=tk.X, pady=(0, 2))
        canvas_title_frame.pack_propagate(False)
        
        canvas_title = ttk.Label(canvas_title_frame, text="이미지 미리보기 및 편집")
        canvas_title.pack(anchor=tk.W)
        
        self.image_canvas = ImageCanvas(canvas_frame, self.on_canvas_modified, self.show_page)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 캔버스에 페이지 이미지 목록 전달
        self.image_canvas.page_images = self.page_images
        
        bottom_frame = ttk.Frame(main_frame, height=50)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        bottom_frame.pack_propagate(False)
        
        self.progress_var = tk.StringVar(value="PDF 파일을 선택하세요")
        progress_label = ttk.Label(bottom_frame, textvariable=self.progress_var)
        progress_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.progress_bar = ttk.Progressbar(bottom_frame, mode='determinate', maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.detect_btn = ttk.Button(button_frame, text="문제 감지", command=self.detect_questions)
        self.detect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.split_btn = ttk.Button(button_frame, text="문제 분할", command=self.split_questions)
        self.split_btn.pack(side=tk.LEFT)
        
        # 첫 번째 모델 자동 로드
        self._initialize_first_model()
    
    def _initialize_first_model(self):
        """첫 번째 모델을 자동으로 로드합니다."""
        try:
            # models 폴더에서 첫 번째 .pt 파일 찾기 (exe 파일 지원)
            models_dir = Path.cwd() / "models"
            
            # exe 파일인 경우 exe 디렉토리에서 찾기
            import sys
            if getattr(sys, 'frozen', False):
                exe_dir = Path(sys.executable).parent
                models_dir = exe_dir / "models"
            
            if models_dir.exists():
                pt_files = list(models_dir.glob("*.pt"))
                if pt_files:
                    first_model = pt_files[0].name
                    
                    # detector 생성
                    from ..utils.question_detector import QuestionDetector
                    self.detector = QuestionDetector(first_model)
                    
                    # settings_panel의 detector 참조 업데이트
                    self.settings_panel.detector = self.detector
                    
                    # 설정 패널의 모델 선택 업데이트
                    self.settings_panel.selected_model_var.set(first_model)
                    
                    # 설정 패널의 모델 정보 즉시 업데이트
                    self.settings_panel.update_model_info()
                else:
                    print("models 폴더에 .pt 파일이 없습니다.")
            else:
                print("models 폴더를 찾을 수 없습니다.")
        except Exception as e:
            print(f"모델 초기화 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="PDF 파일 열기", command=self.select_pdf_file)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="설정", command=self.show_settings)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.show_help)
        help_menu.add_command(label="정보", command=self.show_about)
    
    def select_pdf_file(self):
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.progress_var.set(f"선택된 파일: {Path(file_path).name}")
            self.update_ui_state()
    
    def on_settings_changed(self):
        # 모델 변경 확인
        settings = self.settings_panel.get_settings()
        selected_model = settings.get('selected_model')
        
        if selected_model and selected_model != "모델 없음":
            # detector가 없으면 생성
            if not hasattr(self, 'detector') or self.detector is None:
                from ..utils.question_detector import QuestionDetector
                self.detector = QuestionDetector()
                # settings_panel의 detector 참조 업데이트
                self.settings_panel.detector = self.detector
            
            # 현재 로드된 모델과 다른 경우 모델 변경
            current_model_info = self.detector.get_model_info()
            if current_model_info['name'] != selected_model:
                success = self.detector.change_model(selected_model)
                if success:
                    # 설정 패널의 모델 정보 즉시 업데이트
                    self.settings_panel.update_model_info()
        
        self.processed = False
        self.update_ui_state()
    
    def on_canvas_modified(self):
        """캔버스에서 박스가 편집되었을 때 호출됩니다."""
        # 편집된 문제 목록을 가져와서 업데이트
        if hasattr(self, 'image_canvas') and self.image_canvas:
            modified_questions = self.image_canvas.get_modified_questions()
            if modified_questions:
                self.questions = modified_questions
                pass
    
    def detect_questions(self):
        if not self.current_pdf_path:
            messagebox.showwarning("경고", "PDF 파일을 먼저 선택하세요.")
            return
        
        thread = threading.Thread(target=self._detect_questions_thread)
        thread.daemon = True
        thread.start()
    
    def _detect_questions_thread(self):
        try:
            self.root.after(0, self._start_progress)
            self.root.after(0, lambda: self._update_progress(5, "PDF 파일을 분석 중입니다..."))
            
            if not Path(self.current_pdf_path).exists():
                raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {self.current_pdf_path}")
            
            if self.detector is None:
                # 선택된 모델로 초기화
                settings = self.settings_panel.get_settings()
                selected_model = settings.get('selected_model')
                
                if selected_model and selected_model != "모델 없음":
                    self.detector = QuestionDetector(selected_model)
                else:
                    self.detector = QuestionDetector()
                
                model_info = self.detector.get_model_info()
            
            self.root.after(0, lambda: self._update_progress(10, "모델을 로드 중입니다..."))
            
            settings = self.settings_panel.get_settings()
            
            import tempfile
            self.temp_output = tempfile.mkdtemp()
            
            def progress_callback(progress, message):
                self.root.after(0, lambda: self._update_progress(progress, message))
            
            self.questions, self.page_images = self.detector.process_pdf(
                self.current_pdf_path, 
                self.temp_output, 
                settings['dpi'], 
                settings['confidence'],
                progress_callback
            )
            
            # 캔버스에 페이지 이미지 목록 업데이트
            self.image_canvas.page_images = self.page_images
            
            self.processed = True
            
            self.root.after(0, self._stop_progress)
            self.root.after(0, lambda: self.progress_var.set(f"문제 감지 완료: {len(self.questions)}개 문제 발견"))
            self.root.after(0, self.update_ui_state)
            
            if self.page_images:
                self.root.after(200, lambda: self.show_page(1))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self._stop_progress)
            self.root.after(0, lambda: messagebox.showerror("오류", f"문제 감지 중 오류가 발생했습니다:\n{error_msg}"))
    
    def split_questions(self):
        if not self.processed or not self.questions:
            messagebox.showwarning("경고", "먼저 문제 감지를 실행하세요.")
            return
        
        # outputs 폴더가 없으면 생성
        outputs_dir = Path.cwd() / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        output_dir = filedialog.askdirectory(
            title="내보낼 폴더 선택",
            initialdir=outputs_dir
        )
        
        if not output_dir:
            return
        
        thread = threading.Thread(target=self._split_questions_thread, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _split_questions_thread(self, output_dir):
        try:
            self.root.after(0, self._start_progress)
            self.root.after(0, lambda: self._update_progress(10, "문제 분할을 시작합니다..."))
            
            if self.pdf_generator is None:
                self.pdf_generator = PDFGenerator()
            
            settings = self.settings_panel.get_settings()
            output_formats = settings['output_formats']
            
            created_files = []
            
            # 개별 이미지 생성 (한 번만 생성하고 재사용)
            individual_images = None
            if any([output_formats["개별 이미지"], output_formats["개별 PDF"], output_formats["그룹 PDF"]]):
                self.root.after(0, lambda: self._update_progress(20, "개별 이미지 생성 중..."))
                # 임시 폴더에 이미지 생성
                temp_images_dir = Path(output_dir) / "temp_images"
                temp_images_dir.mkdir(exist_ok=True)
                individual_images = self._regenerate_question_images(str(temp_images_dir))
            
            self.root.after(0, lambda: self._update_progress(30, "개별 이미지 생성 중..."))
            if output_formats["개별 이미지"]:
                # 개별 이미지 폴더 생성
                images_dir = Path(output_dir) / "개별_이미지"
                images_dir.mkdir(exist_ok=True)
                # 임시 이미지들을 개별 이미지 폴더로 복사
                for i, img_path in enumerate(individual_images):
                    import shutil
                    new_path = images_dir / f"문제_{i+1:03d}.png"
                    shutil.copy2(img_path, new_path)
                    created_files.append(str(new_path))
            
            self.root.after(0, lambda: self._update_progress(40, "개별 PDF 생성 중..."))
            if output_formats["개별 PDF"]:
                # 개별 PDF 폴더 생성
                pdfs_dir = Path(output_dir) / "개별_PDF"
                pdfs_dir.mkdir(exist_ok=True)
                # 개별 PDF 생성
                pdf_files = self.pdf_generator.create_individual_pdfs(individual_images, str(pdfs_dir))
                created_files.extend(pdf_files)
            
            self.root.after(0, lambda: self._update_progress(60, "그룹 PDF 생성 중..."))
            if output_formats["그룹 PDF"]:
                # 그룹 PDF 폴더 생성
                groups_dir = Path(output_dir) / "그룹_PDF"
                groups_dir.mkdir(exist_ok=True)
                # 그룹 생성 및 PDF 생성
                groups = self.pdf_generator.group_questions(individual_images, settings['group_size'])
                group_files = self.pdf_generator.create_grouped_pdfs(groups, str(groups_dir))
                created_files.extend(group_files)
            
            self.root.after(0, lambda: self._update_progress(80, "전체 문제집 생성 중..."))
            if output_formats["전체 문제집"]:
                workbook_path = Path(output_dir) / "전체_문제집.pdf"
                self.pdf_generator.create_exam_workbook(self.questions, {}, str(workbook_path))
                created_files.append(str(workbook_path))
            
            self.root.after(0, lambda: self._update_progress(90, "셔플 문제집 생성 중..."))
            if output_formats.get("셔플 문제집", False):
                shuffled_path = Path(output_dir) / "셔플_문제집.pdf"
                self.pdf_generator.create_shuffled_workbook(
                    self.questions, {}, str(shuffled_path), settings.get('shuffle_seed')
                )
                created_files.append(str(shuffled_path))
            
            # 임시 폴더 정리
            if individual_images:
                import shutil
                temp_images_dir = Path(output_dir) / "temp_images"
                if temp_images_dir.exists():
                    shutil.rmtree(temp_images_dir)
            
            self.root.after(0, self._stop_progress)
            self.root.after(0, lambda: self.progress_var.set(f"문제 분할 완료: {len(created_files)}개 파일 생성"))
            
            messagebox.showinfo("완료", f"문제 분할이 완료되었습니다!\n생성된 파일: {len(created_files)}개\n저장 위치: {output_dir}")
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self._stop_progress)
            self.root.after(0, lambda: messagebox.showerror("오류", f"문제 분할 중 오류가 발생했습니다:\n{error_msg}"))
    
    def show_page(self, page_num):
        """특정 페이지를 표시합니다."""
        if 1 <= page_num <= len(self.page_images):
            page_image_path = self.page_images[page_num - 1]
            # 전체 문제 목록을 전달 (페이지별 필터링은 canvas에서 처리)
            self.image_canvas.load_image(page_image_path, page_num, self.questions)
    
    def _regenerate_question_images(self, output_dir):
        """편집된 박스 정보를 사용하여 개별 문제 이미지를 재생성합니다."""
        import os
        
        question_images = []
        
        for i, question in enumerate(self.questions):
            try:
                # 원본 페이지 이미지 로드
                page_image_path = self.page_images[question['page'] - 1]
                img = cv2.imread(page_image_path)
                if img is None:
                    continue
                
                h, w = img.shape[:2]
                
                # 편집된 박스 좌표를 픽셀 좌표로 변환
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
                
                question_images.append(question_img_path)
                
            except Exception as e:
                # 실패 시 기존 이미지 경로 사용
                if 'image_path' in question:
                    question_images.append(question['image_path'])
        
        return question_images
    
    def _start_progress(self):
        self.progress_bar.start()
    
    def _stop_progress(self):
        self.progress_bar.stop()
    
    def _update_progress(self, value, message=None):
        self.progress_bar['value'] = value
        if message:
            self.progress_var.set(message)
    
    def on_window_resize(self, event):
        if hasattr(self, 'image_canvas'):
            self.image_canvas.display_image()
    
    def update_ui_state(self):
        has_file = self.current_pdf_path is not None
        self.detect_btn['state'] = 'normal' if has_file else 'disabled'
        self.split_btn['state'] = 'normal' if self.processed else 'disabled'
    
    def show_settings(self):
        """설정 다이얼로그를 표시합니다."""
        # 설정 패널의 모델 정보 업데이트
        self.settings_panel.refresh_model_info()
    
    def show_help(self):
        help_text = """
ExamSplitter 사용법:

1. PDF 파일 선택: "PDF 파일 선택" 버튼을 클릭하여 시험지 PDF를 업로드합니다.

2. 설정 조정: 왼쪽 설정 패널에서 DPI, 감지 신뢰도, 출력 형식을 조정합니다.

3. 문제 감지: "문제 감지" 버튼을 클릭하여 PDF에서 문제 영역을 자동으로 감지합니다.

4. 편집 (선택사항): 오른쪽 캔버스에서 감지된 박스를 드래그하여 크기나 위치를 조정할 수 있습니다.

5. 문제 분할: "문제 분할" 버튼을 클릭하여 선택한 형식으로 문제를 분할합니다.

6. 결과 확인: 생성된 파일들을 지정한 폴더에서 확인할 수 있습니다.
        """
        messagebox.showinfo("사용법", help_text)
    
    def show_about(self):
        about_text = """
ExamSplitter v1.0

PDF 시험지 문제 분할 도구

기술 스택:
- Python 3.8+
- YOLOv8 (문제 감지)
- PyMuPDF (PDF 처리)
- tkinter (GUI)

개발자: devksy(Kim suyun)
라이선스: MIT
        """
        messagebox.showinfo("정보", about_text)
    
    def cleanup(self):
        """리소스 정리 작업을 수행합니다."""
        try:
            # 임시 출력 디렉토리 정리
            if hasattr(self, 'temp_output') and self.temp_output:
                import shutil
                temp_path = Path(self.temp_output)
                if temp_path.exists():
                    shutil.rmtree(temp_path)
            
            # detector 정리
            if hasattr(self, 'detector') and self.detector:
                if hasattr(self.detector, 'cleanup'):
                    self.detector.cleanup()
            
            # pdf_generator 정리
            if hasattr(self, 'pdf_generator') and self.pdf_generator:
                if hasattr(self.pdf_generator, 'cleanup'):
                    self.pdf_generator.cleanup()
            
            # 캔버스 정리
            if hasattr(self, 'image_canvas') and self.image_canvas:
                if hasattr(self.image_canvas, 'cleanup'):
                    self.image_canvas.cleanup()
            
            # 설정 패널 정리
            if hasattr(self, 'settings_panel') and self.settings_panel:
                if hasattr(self.settings_panel, 'cleanup'):
                    self.settings_panel.cleanup()
                    
        except Exception as e:
            # 정리 작업 중 오류가 발생해도 무시
            pass 