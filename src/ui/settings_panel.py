#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 패널 클래스
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from ..config import DEFAULT_DPI, DEFAULT_CONFIDENCE, DEFAULT_GROUP_SIZE

class SettingsPanel(ttk.LabelFrame):
    def __init__(self, parent, callback=None, detector=None):
        super().__init__(parent, text="설정", padding=5)
        self.callback = callback
        self.detector = detector
        
        self.dpi_var = tk.IntVar(value=DEFAULT_DPI)
        self.confidence_var = tk.DoubleVar(value=DEFAULT_CONFIDENCE)
        self.group_size_var = tk.IntVar(value=DEFAULT_GROUP_SIZE)
        
        self.output_formats = {
            "개별 이미지": tk.BooleanVar(value=True),
            "개별 PDF": tk.BooleanVar(value=True),
            "그룹 PDF": tk.BooleanVar(value=False),
            "전체 문제집": tk.BooleanVar(value=False),
            "셔플 문제집": tk.BooleanVar(value=False)
        }
        
        self.shuffle_seed_var = tk.IntVar(value=42)
        self.use_random_seed_var = tk.BooleanVar(value=False)
        
        # 모델 선택 변수
        self.selected_model_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        basic_frame = ttk.LabelFrame(self, text="기본 설정", padding=3)
        basic_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(basic_frame, text="DPI 설정:").pack(anchor=tk.W)
        dpi_scale = ttk.Scale(basic_frame, from_=150, to=600, variable=self.dpi_var, 
                             orient=tk.HORIZONTAL, command=self.on_setting_changed)
        dpi_scale.pack(fill=tk.X, pady=(0, 5))
        self.dpi_label = ttk.Label(basic_frame, text=f"현재: {self.dpi_var.get()}")
        self.dpi_label.pack(anchor=tk.W)
        
        ttk.Label(basic_frame, text="감지 신뢰도:").pack(anchor=tk.W, pady=(10, 0))
        confidence_scale = ttk.Scale(basic_frame, from_=0.1, to=1.0, variable=self.confidence_var,
                                   orient=tk.HORIZONTAL, command=self.on_setting_changed)
        confidence_scale.pack(fill=tk.X, pady=(0, 5))
        self.confidence_label = ttk.Label(basic_frame, text=f"현재: {self.confidence_var.get():.1f}")
        self.confidence_label.pack(anchor=tk.W)
        
        output_frame = ttk.LabelFrame(self, text="출력 형식", padding=3)
        output_frame.pack(fill=tk.X, pady=(0, 5))
        
        for format_name, var in self.output_formats.items():
            cb = ttk.Checkbutton(output_frame, text=format_name, variable=var, 
                               command=self.on_setting_changed)
            cb.pack(anchor=tk.W, pady=1)
        
        group_frame = ttk.LabelFrame(self, text="그룹 설정", padding=3)
        group_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(group_frame, text="그룹당 문제 수:").pack(anchor=tk.W)
        group_spinbox = ttk.Spinbox(group_frame, from_=1, to=20, textvariable=self.group_size_var,
                                   command=self.on_setting_changed)
        group_spinbox.pack(fill=tk.X, pady=(0, 5))
        
        shuffle_frame = ttk.LabelFrame(self, text="셔플 설정", padding=3)
        shuffle_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Checkbutton(shuffle_frame, text="고정 시드 사용", variable=self.use_random_seed_var,
                       command=self.on_setting_changed).pack(anchor=tk.W, pady=1)
        
        seed_frame = ttk.Frame(shuffle_frame)
        seed_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(seed_frame, text="시드 값:").pack(side=tk.LEFT)
        seed_spinbox = ttk.Spinbox(seed_frame, from_=1, to=9999, textvariable=self.shuffle_seed_var,
                                  command=self.on_setting_changed, width=10)
        seed_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(shuffle_frame, text="※ 고정 시드를 사용하면 항상 같은 순서로 셔플됩니다", 
                 font=("", 8), foreground="gray").pack(anchor=tk.W, pady=(5, 0))
        
        model_frame = ttk.LabelFrame(self, text="모델 설정", padding=3)
        model_frame.pack(fill=tk.X)
        
        # 모델 선택 프레임
        model_select_frame = ttk.Frame(model_frame)
        model_select_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(model_select_frame, text="모델 선택:").pack(side=tk.LEFT)
        self.model_combobox = ttk.Combobox(model_select_frame, textvariable=self.selected_model_var, 
                                          state="readonly", width=20)
        self.model_combobox.pack(side=tk.LEFT, padx=(5, 0))
        self.model_combobox.bind("<<ComboboxSelected>>", self.on_model_changed)
        
        # 모델 정보 라벨
        self.model_info_label = ttk.Label(model_frame, text="모델 로딩 중...")
        self.model_info_label.pack(anchor=tk.W)
        
        self.update_available_models()
        self.update_model_info()
    
    def on_setting_changed(self, *args):
        self.dpi_label.config(text=f"현재: {self.dpi_var.get()}")
        self.confidence_label.config(text=f"현재: {self.confidence_var.get():.1f}")
        
        if self.callback:
            self.callback()
    
    def on_model_changed(self, event=None):
        """모델이 변경되었을 때 호출됩니다."""
        # 콜백 즉시 호출 (모델 변경 처리)
        if self.callback:
            self.callback()
        
        # 모델 정보 업데이트 (약간의 지연 후)
        self.after(200, self.update_model_info)
    
    def update_available_models(self):
        """사용 가능한 모델들을 찾아서 콤보박스를 업데이트합니다."""
        try:
            models_dir = Path.cwd() / "models"
            if not models_dir.exists():
                return
            
            # .pt 파일들 찾기
            model_files = list(models_dir.glob("*.pt"))
            model_names = [f.name for f in model_files]
            
            if not model_names:
                model_names = ["모델 없음"]
            
            # 콤보박스 업데이트
            self.model_combobox['values'] = model_names
            
            # 기본값 설정 (첫 번째 모델 또는 현재 선택된 모델)
            if not self.selected_model_var.get() or self.selected_model_var.get() not in model_names:
                if model_names and model_names[0] != "모델 없음":
                    self.selected_model_var.set(model_names[0])
                else:
                    self.selected_model_var.set("모델 없음")
            
        except Exception as e:
            self.model_combobox['values'] = ["모델 없음"]
            self.selected_model_var.set("모델 없음")
    
    def update_model_info(self):
        try:
            selected_model = self.selected_model_var.get()
            if not selected_model or selected_model == "모델 없음":
                self.model_info_label.config(text="선택된 모델 없음")
                return
            
            # 선택된 모델 파일 정보
            models_dir = Path.cwd() / "models"
            model_path = models_dir / selected_model
            
            if not model_path.exists():
                self.model_info_label.config(text=f"모델 파일을 찾을 수 없음: {selected_model}")
                return
            
            # 파일 크기 계산
            size_mb = model_path.stat().st_size / (1024 * 1024)
            
            # 현재 로드된 모델과 비교
            if self.detector:
                current_model_info = self.detector.get_model_info()
                
                if current_model_info['loaded'] and current_model_info['name'] == selected_model:
                    status = "로드됨 ✅"
                else:
                    status = "로드 안됨 ⚠️"
            else:
                status = "로드 안됨 ⚠️"
            
            info_text = f"선택된 모델: {selected_model}\n크기: {size_mb:.1f}MB\n상태: {status}"
            
            self.model_info_label.config(text=info_text)
            
        except Exception as e:
            self.model_info_label.config(text=f"모델 정보 오류: {str(e)}")
    
    def refresh_model_info(self):
        """모델 정보를 새로고침합니다."""
        self.update_available_models()
        self.update_model_info()
    
    def get_settings(self):
        return {
            'dpi': self.dpi_var.get(),
            'confidence': self.confidence_var.get(),
            'group_size': self.group_size_var.get(),
            'output_formats': {name: var.get() for name, var in self.output_formats.items()},
            'shuffle_seed': self.shuffle_seed_var.get() if self.use_random_seed_var.get() else None,
            'selected_model': self.selected_model_var.get()
        }
    
    def cleanup(self):
        """리소스 정리 작업을 수행합니다."""
        try:
            # detector 참조 해제
            if hasattr(self, 'detector'):
                self.detector = None
            
            # 콜백 참조 해제
            if hasattr(self, 'callback'):
                self.callback = None
            
        except Exception as e:
            # 정리 작업 중 오류가 발생해도 무시
            pass 