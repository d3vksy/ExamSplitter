"""
ExamSplitter 메인 애플리케이션
"""

import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import ApplicationConfig
from src.utils.logger import setup_logging, get_logger
from src.core.exceptions import ExamSplitterError
from src.ui.main_window import MainWindow


class ExamSplitterApp:
    """ExamSplitter 메인 애플리케이션 클래스"""
    
    def __init__(self, config: Optional[ApplicationConfig] = None):
        """애플리케이션을 초기화합니다.
        
        Args:
            config: 애플리케이션 설정 (None이면 기본 설정 사용)
        """
        self.logger = get_logger(__name__)
        
        # 설정 관리자를 통해 일관된 설정 사용
        if config is None:
            from src.config.settings import get_app_config
            self.config = get_app_config()
        else:
            self.config = config
        
        # 로깅 설정
        self._setup_logging()
        
        # Tkinter 루트 윈도우
        self.root: Optional[tk.Tk] = None
        self.main_window: Optional[MainWindow] = None
        
        self.logger.info("ExamSplitter 애플리케이션 초기화 완료")
    
    def _create_default_config(self) -> ApplicationConfig:
        """기본 설정을 생성합니다. (하위 호환성을 위해 유지)"""
        from src.config.defaults import DefaultSettings
        defaults = DefaultSettings.get_app_config_defaults()
        return ApplicationConfig(**defaults)
    
    def _setup_logging(self) -> None:
        """로깅을 설정합니다."""
        log_file = self.config.project_root / "logs" / "app.log"
        setup_logging(
            log_level=self.config.log_level,
            log_format=self.config.log_format,
            log_file=log_file,
            console_output=True
        )
        self.logger.info("로깅 설정 완료")
    
    def run(self) -> None:
        """애플리케이션을 실행합니다."""
        try:
            self.logger.info("애플리케이션 시작")
            
            # Tkinter 루트 윈도우 생성
            self.root = tk.Tk()
            self._setup_root_window()
            
            # 메인 윈도우 생성
            self.main_window = MainWindow(self.root, self.config)
            
            # 이벤트 바인딩
            self._bind_events()
            
            self.logger.info("UI 초기화 완료")
            
            # 메인 루프 시작
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"애플리케이션 실행 중 오류 발생: {e}", exc_info=True)
            self._show_error_dialog("애플리케이션 시작 실패", str(e))
            raise
    
    def _setup_root_window(self) -> None:
        """루트 윈도우를 설정합니다."""
        if not self.root:
            return
        
        # 윈도우 제목
        self.root.title("ExamSplitter - PDF 시험지 문제 분할 도구")
        
        # 윈도우 크기 및 위치 설정
        self._center_window()
        
        # 최소 크기 설정
        self.root.minsize(800, 600)
        
    
    def _center_window(self) -> None:
        """윈도우를 화면 중앙에 배치합니다."""
        if not self.root:
            return
        
        # 화면 크기 가져오기
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 윈도우 크기 계산 (화면의 80% 크기, 최소/최대 제한)
        window_width = min(max(int(screen_width * 0.8), 800), 1400)
        window_height = min(max(int(screen_height * 0.8), 600), 1000)
        
        # 중앙 위치 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 윈도우 크기 및 위치 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _bind_events(self) -> None:
        """이벤트를 바인딩합니다."""
        if not self.root:
            return
        
        # 윈도우 종료 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 키보드 단축키
        self.root.bind("<Control-q>", self._on_closing)
        self.root.bind("<Control-w>", self._on_closing)
    
    def _on_closing(self, event=None) -> None:
        """애플리케이션 종료 처리"""
        try:
            self.logger.info("애플리케이션 종료 요청")
            
            # 정리 작업 수행
            self._cleanup()
            
            # 윈도우 종료
            if self.root:
                self.root.quit()
                self.root.destroy()
            
            self.logger.info("애플리케이션 종료 완료")
            
        except Exception as e:
            self.logger.error(f"애플리케이션 종료 중 오류: {e}")
            # 강제 종료
            if self.root:
                self.root.destroy()
    
    def _cleanup(self) -> None:
        """정리 작업을 수행합니다."""
        try:
            # 임시 파일 정리
            self._cleanup_temp_files()
            
            # 리소스 해제
            if self.main_window:
                self.main_window.cleanup()
            
        except Exception as e:
            self.logger.error(f"정리 작업 중 오류: {e}")
    
    def _cleanup_temp_files(self) -> None:
        """임시 파일들을 정리합니다."""
        try:
            temp_dir = self.config.temp_directory
            if temp_dir.exists():
                # 임시 파일들 삭제
                for temp_file in temp_dir.glob("*"):
                    if temp_file.is_file():
                        temp_file.unlink()
                        self.logger.debug(f"임시 파일 삭제: {temp_file}")
            
        except Exception as e:
            self.logger.warning(f"임시 파일 정리 중 오류: {e}")
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """오류 다이얼로그를 표시합니다."""
        try:
            messagebox.showerror(title, message)
        except Exception as e:
            pass


def main():
    """메인 함수"""
    try:
        # 애플리케이션 생성 및 실행
        app = ExamSplitterApp()
        app.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass


if __name__ == "__main__":
    main() 