#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지 캔버스 위젯 클래스
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path

class ImageCanvas(ttk.Frame):
    def __init__(self, parent, callback=None, page_callback=None):
        super().__init__(parent)
        self.callback = callback
        self.page_callback = page_callback
        
        self.current_image = None
        self.current_photo = None
        self.current_page = 1
        self.all_questions = []  # 전체 문제 목록
        self.page_images = []
        self.scale_factor = None
        self.original_size = (0, 0)
        self._last_canvas_size = None
        
        self.boxes = []  # 현재 페이지 박스들
        self.selected_box = None
        self.drag_start = None
        self.resize_mode = None
        self.resize_handle_size = 8
        
        self.setup_ui()
        self.bind_events()
    
    def setup_ui(self):
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white',
                               yscrollcommand=self.v_scrollbar.set,
                               xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(nav_frame, text="◀", command=self.prev_page).pack(side=tk.LEFT)
        self.page_label = ttk.Label(nav_frame, text="페이지 1")
        self.page_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="▶", command=self.next_page).pack(side=tk.LEFT)
        
        zoom_frame = ttk.Frame(self)
        zoom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(zoom_frame, text="확대", command=self.zoom_in).pack(side=tk.LEFT)
        ttk.Button(zoom_frame, text="축소", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="실제 크기", command=self.zoom_fit).pack(side=tk.LEFT)
    
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Motion>", self.on_mouse_move)
    
    def load_image(self, image_path, page_num, questions):
        try:
            if not Path(image_path).exists():
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            
            if self.current_image is not None:
                self.current_image.close()
                self.current_image = None
            
            self.current_image = Image.open(image_path).convert('RGB')
            self.original_size = self.current_image.size
            self.current_page = page_num
            self.current_page_image_path = image_path
            
            # 전체 문제 목록 저장 (항상 업데이트)
            self.all_questions = questions
            
            # 현재 페이지의 박스들만 추출
            self.boxes = []
            for q in self.all_questions:
                if q['page'] == page_num:
                    self.boxes.append(q['box'].copy())
            
            self.scale_factor = None
            self._last_canvas_size = None
            
            self.display_image()
            self.page_label.config(text=f"페이지 {page_num}")
            
        except Exception as e:
            pass
    
    def display_image(self):
        if self.current_image is None:
            return
        
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
            
            img_width, img_height = self.current_image.size
            
            if (self.scale_factor is None or 
                not hasattr(self, '_last_canvas_size') or 
                self._last_canvas_size != (canvas_width, canvas_height)):
                
                scale_x = (canvas_width - 20) / img_width
                scale_y = (canvas_height - 20) / img_height
                self.scale_factor = min(scale_x, scale_y)
                self._last_canvas_size = (canvas_width, canvas_height)
            
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            
            resized_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.current_photo = ImageTk.PhotoImage(resized_image)
            
            self.canvas.delete("all")
            
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.current_photo, tags="image")
            self.draw_boxes(x_offset, y_offset)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            pass
    
    def draw_boxes(self, x_offset=0, y_offset=0):
        if self.scale_factor is None:
            return
            
        for i, box in enumerate(self.boxes):
            try:
                x1, y1, x2, y2 = box
                
                # 정규화된 좌표를 픽셀 좌표로 변환
                img_width, img_height = self.original_size
                pixel_x1 = x1 * img_width
                pixel_y1 = y1 * img_height
                pixel_x2 = x2 * img_width
                pixel_y2 = y2 * img_height
                
                # 스케일 적용
                scaled_x1 = pixel_x1 * self.scale_factor + x_offset
                scaled_y1 = pixel_y1 * self.scale_factor + y_offset
                scaled_x2 = pixel_x2 * self.scale_factor + x_offset
                scaled_y2 = pixel_y2 * self.scale_factor + y_offset
                
                # 박스 그리기
                self.canvas.create_rectangle(
                    scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                    outline="green", width=2, tags=f"box_{i}"
                )
                
                # 라벨 그리기
                self.canvas.create_text(
                    scaled_x1 + 10, scaled_y1 - 10,
                    text=str(i + 1), fill="green", font=("Arial", 12, "bold"),
                    tags=f"label_{i}"
                )
                
                # 선택된 박스면 핸들 그리기
                if i == self.selected_box:
                    self.draw_resize_handles(scaled_x1, scaled_y1, scaled_x2, scaled_y2, i)
                        
            except Exception as e:
                pass
    
    def draw_resize_handles(self, x1, y1, x2, y2, box_index):
        handle_size = self.resize_handle_size
        
        handles = [
            (x1 - handle_size//2, y1 - handle_size//2, "nw"),
            (x2 - handle_size//2, y1 - handle_size//2, "ne"),
            (x1 - handle_size//2, y2 - handle_size//2, "sw"),
            (x2 - handle_size//2, y2 - handle_size//2, "se")
        ]
        
        for hx, hy, mode in handles:
            self.canvas.create_rectangle(
                hx, hy, hx + handle_size, hy + handle_size,
                fill="red", outline="white", tags=f"handle_{box_index}_resize_{mode}"
            )
    
    def on_mouse_down(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        clicked_items = self.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        self.selected_box = None
        self.resize_mode = None
        
        # 핸들 클릭을 먼저 확인 (박스보다 우선순위)
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("handle_"):
                    parts = tag.split("_")
                    if len(parts) >= 4:  # handle_boxIndex_resize_mode
                        box_index = int(parts[1])
                        self.selected_box = box_index
                        self.resize_mode = f"resize_{parts[3]}"  # resize_nw, resize_ne, resize_sw, resize_se
                        self.drag_start = (canvas_x, canvas_y)
                        return
        
        # 박스 클릭 확인
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("box_"):
                    box_index = int(tag.split("_")[1])
                    self.selected_box = box_index
                    self.drag_start = (canvas_x, canvas_y)
                    self.resize_mode = "move"
                    return
    
    def on_mouse_drag(self, event):
        if self.selected_box is None or self.drag_start is None:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        dx = canvas_x - self.drag_start[0]
        dy = canvas_y - self.drag_start[1]
        
        if self.scale_factor is None:
            return
        
        # 이미지 크기로 정규화
        img_width, img_height = self.original_size
        scale_inv = 1.0 / self.scale_factor
        
        # 픽셀 단위 변화량을 정규화된 좌표로 변환
        norm_dx = dx * scale_inv / img_width
        norm_dy = dy * scale_inv / img_height
        
        # 박스 좌표 업데이트
        if self.resize_mode == "move":
            self.boxes[self.selected_box][0] += norm_dx
            self.boxes[self.selected_box][1] += norm_dy
            self.boxes[self.selected_box][2] += norm_dx
            self.boxes[self.selected_box][3] += norm_dy
        elif self.resize_mode == "resize_nw":
            self.boxes[self.selected_box][0] += norm_dx
            self.boxes[self.selected_box][1] += norm_dy
        elif self.resize_mode == "resize_ne":
            self.boxes[self.selected_box][2] += norm_dx
            self.boxes[self.selected_box][1] += norm_dy
        elif self.resize_mode == "resize_sw":
            self.boxes[self.selected_box][0] += norm_dx
            self.boxes[self.selected_box][3] += norm_dy
        elif self.resize_mode == "resize_se":
            self.boxes[self.selected_box][2] += norm_dx
            self.boxes[self.selected_box][3] += norm_dy
        
        self.drag_start = (canvas_x, canvas_y)
        self.update_boxes_display()
    
    def on_mouse_move(self, event):
        """마우스 이동 시 커서 변경"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(canvas_x-3, canvas_y-3, canvas_x+3, canvas_y+3)
        
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("box_"):
                    self.canvas.config(cursor="fleur")
                    return
                elif tag.startswith("handle_"):
                    self.canvas.config(cursor="sizing")
                    return
        
        self.canvas.config(cursor="")
    
    def on_double_click(self, event):
        """더블클릭으로 박스 활성화"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        clicked_items = self.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("box_"):
                    box_index = int(tag.split("_")[1])
                    self.selected_box = box_index
                    self.resize_mode = "move"
                    return
    
    def on_mouse_up(self, event):
        if self.selected_box is not None and self.callback:
            self.callback()
        self.drag_start = None
        self.resize_mode = None
    
    def on_canvas_resize(self, event):
        self.display_image()
    
    def update_boxes_display(self):
        """박스만 다시 그리기"""
        if self.scale_factor is None:
            return
            
        # 기존 박스, 라벨, 핸들 삭제
        for i in range(len(self.boxes)):
            self.canvas.delete(f"box_{i}")
            self.canvas.delete(f"label_{i}")
            for mode in ["nw", "ne", "sw", "se"]:
                self.canvas.delete(f"handle_{i}_resize_{mode}")
        
        # 박스 다시 그리기
        x_offset = (self.canvas.winfo_width() - int(self.current_image.size[0] * self.scale_factor)) // 2
        y_offset = (self.canvas.winfo_height() - int(self.current_image.size[1] * self.scale_factor)) // 2
        self.draw_boxes(x_offset, y_offset)
    
    def prev_page(self):
        if self.page_callback and self.current_page > 1:
            self.page_callback(self.current_page - 1)
    
    def next_page(self):
        if self.page_callback and self.current_page < len(self.page_images):
            self.page_callback(self.current_page + 1)
    
    def zoom_in(self):
        if self.scale_factor:
            self.scale_factor *= 1.2
            self.display_image()
    
    def zoom_out(self):
        if self.scale_factor:
            self.scale_factor /= 1.2
            self.display_image()
    
    def zoom_fit(self):
        self.scale_factor = None
        self.display_image()
    
    def get_modified_questions(self):
        """편집된 문제 목록을 반환합니다."""
        # 현재 페이지 박스들을 전체 문제 목록에 업데이트
        updated_questions = []
        
        # 현재 페이지의 문제들만 필터링
        current_page_questions = [q for q in self.all_questions if q['page'] == self.current_page]
        
        # 현재 페이지 문제들을 boxes 순서대로 업데이트
        for i, box in enumerate(self.boxes):
            if i < len(current_page_questions):
                updated_q = current_page_questions[i].copy()
                updated_q['box'] = box.copy()
                updated_questions.append(updated_q)
        
        # 다른 페이지 문제들은 그대로 유지
        for q in self.all_questions:
            if q['page'] != self.current_page:
                updated_questions.append(q)
        
        return updated_questions
    
    def show_page(self, page_num):
        """특정 페이지를 표시합니다."""
        if hasattr(self, 'page_images') and 1 <= page_num <= len(self.page_images):
            page_image_path = self.page_images[page_num - 1]
            self.load_image(page_image_path, page_num, self.all_questions)
    
    def cleanup(self):
        """리소스 정리 작업을 수행합니다."""
        try:
            # 현재 이미지 해제
            if hasattr(self, 'current_image') and self.current_image is not None:
                self.current_image.close()
                self.current_image = None
            
            # PhotoImage 해제
            if hasattr(self, 'current_photo') and self.current_photo is not None:
                self.current_photo = None
            
            # 캔버스 내용 삭제
            if hasattr(self, 'canvas'):
                self.canvas.delete("all")
            
            # 변수 초기화
            self.boxes = []
            self.selected_box = None
            self.drag_start = None
            self.resize_mode = None
            self.scale_factor = None
            self.original_size = (0, 0)
            self._last_canvas_size = None
            
        except Exception as e:
            # 정리 작업 중 오류가 발생해도 무시
            pass 