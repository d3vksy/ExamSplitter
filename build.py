"""
ExamSplitter PyInstaller 빌드 스크립트
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """명령어를 실행하고 결과를 출력합니다."""
    print(f"{description}")
    print(f"실행 중: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} 완료")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} 실패")
        print(f"오류: {e.stderr}")
        return False

def clean_build_dirs():
    """빌드 디렉토리를 정리합니다."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"{dir_name} 디렉토리 정리 중...")
            shutil.rmtree(dir_name)

def create_release_package(version):
    """릴리즈 패키지를 생성합니다."""
    release_dir = f"ExamSplitter-v{version}"
    
    # 기존 릴리즈 디렉토리 정리
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    # 릴리즈 디렉토리 생성
    os.makedirs(release_dir, exist_ok=True)
    
    # 파일 복사
    files_to_copy = [
        ('dist/ExamSplitter.exe', f'{release_dir}/ExamSplitter.exe'),
        ('README.md', f'{release_dir}/README.md'),
        ('LICENSE', f'{release_dir}/LICENSE'),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"{src} → {dst}")
        else:
            print(f"파일을 찾을 수 없음: {src}")
    
    # models 폴더 복사
    if os.path.exists('models'):
        shutil.copytree('models', f'{release_dir}/models', dirs_exist_ok=True)
        print(f"models/ → {release_dir}/models/")
    
    # ZIP 파일 생성
    zip_name = f"ExamSplitter-v{version}.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    shutil.make_archive(f"ExamSplitter-v{version}", 'zip', release_dir)
    print(f"{zip_name} 생성 완료")
    
    # 릴리즈 디렉토리 정리
    shutil.rmtree(release_dir)
    
    return zip_name

def main():
    """메인 함수"""
    print("ExamSplitter PyInstaller 빌드 시작")
    print("=" * 50)
    
    # 버전 확인
    version = input("배포 버전을 입력하세요 (예: 1.0.0): ").strip()
    if not version:
        print("버전을 입력해주세요.")
        return
    
    # 빌드 디렉토리 정리
    clean_build_dirs()
    
    # PyInstaller 명령어 구성
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ExamSplitter",
        "--add-data=models;models",
        "--add-data=banner.png;.",
        "--icon=banner.png",
        "--hidden-import=ultralytics",
        "--hidden-import=cv2",
        "--hidden-import=fitz",
        "--hidden-import=PIL",
        "--hidden-import=reportlab",
        "--hidden-import=numpy",
        "--hidden-import=tkinter",
        "--clean",
        "main.py"
    ]
    
    # PyInstaller 실행
    if not run_command(" ".join(pyinstaller_cmd), "PyInstaller 빌드"):
        print("빌드 실패")
        return
    
    # 실행 파일 확인
    exe_path = "dist/ExamSplitter.exe"
    if not os.path.exists(exe_path):
        print("실행 파일이 생성되지 않았습니다.")
        return
    
    # 파일 크기 확인
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"실행 파일 크기: {file_size:.2f} MB")
    
    # 릴리즈 패키지 생성
    zip_name = create_release_package(version)
    
    print("=" * 50)
    print("빌드 완료!")
    print(f"실행 파일: {exe_path}")
    print(f"릴리즈 패키지: {zip_name}")
    print(f"파일 크기: {file_size:.2f} MB")

if __name__ == "__main__":
    main() 