import os
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_NAME = "ExamSplitter"
ENTRY_FILE = "main.py"
MODEL_DIR = "models"
BANNER_FILE = "banner.png"


def clean_old_build():
    """Remove previous build folders"""
    for folder in ["build", "dist", PROJECT_NAME, "__pycache__"]:
        if os.path.exists(folder):
            print(f"[INFO] Removing old folder: {folder}")
            shutil.rmtree(folder)
    print("[INFO] Previous build folders cleaned.")


def build_exe():
    """Run PyInstaller to build the executable"""
    banner_abs = Path(BANNER_FILE).resolve()
    if not banner_abs.exists():
        print(f"[WARN] Banner file not found: {banner_abs}")

    cmd = [
        "pyinstaller",
        ENTRY_FILE,
        "--onedir",
        # "--noconsole",  # 콘솔 창 표시하여 오류 확인 가능
        "--clean",
        f"--name={PROJECT_NAME}",
        "--hidden-import=ultralytics",
        "--hidden-import=torch",
        "--hidden-import=torchvision",
        "--hidden-import=onnxruntime",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=pandas",
        "--hidden-import=reportlab",
        "--hidden-import=tkinter",
        "--hidden-import=fitz",
        "--hidden-import=pymupdf",
        "--collect-all=ultralytics",
        "--collect-all=torch",
        f'--add-data="{banner_abs};."',
        "--distpath=dist",
        "--workpath=build",
        "--specpath=build",
        "--log-level=INFO"
    ]

    print("[INFO] Running PyInstaller with command:")
    print(" ".join(cmd))

    start_time = time.time()
    try:
        subprocess.run(" ".join(cmd), shell=True, check=True)
        print(f"[INFO] Build completed in {time.time() - start_time:.1f} seconds")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False


def copy_models_to_dist():
    """Copy the models folder next to the built exe"""
    source_model_dir = Path(MODEL_DIR)
    target_model_dir = Path(f"dist/{PROJECT_NAME}/{MODEL_DIR}")

    if not source_model_dir.exists():
        print(f"[WARN] Models folder not found: {source_model_dir}")
        return False

    try:
        if target_model_dir.exists():
            shutil.rmtree(target_model_dir)
        shutil.copytree(source_model_dir, target_model_dir)
        print(f"[INFO] Models folder copied to: {target_model_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to copy models folder: {e}")
        return False


def compress_with_upx():
    """Optional UPX compression (disabled by default in CI)"""
    exe_path = Path(f"dist/{PROJECT_NAME}/{PROJECT_NAME}.exe")
    if not exe_path.exists():
        print("[ERROR] Executable file not found for UPX compression")
        return False

    original_size = exe_path.stat().st_size / (1024 * 1024)
    print(f"[INFO] Original exe size: {original_size:.2f} MB")

    try:
        subprocess.run(f"upx --best --lzma {exe_path}", shell=True, check=True)
        compressed_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"[INFO] UPX compression completed. New size: {compressed_size:.2f} MB")
        return True
    except subprocess.CalledProcessError:
        print("[WARN] UPX compression failed (ensure UPX is installed if needed)")
        return False


def check_file_size():
    """Check built exe and folder size"""
    exe_path = Path(f"dist/{PROJECT_NAME}/{PROJECT_NAME}.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[INFO] Executable size: {size_mb:.2f} MB")
    else:
        print("[ERROR] Executable file does not exist.")


def main():
    print("[INFO] Starting ExamSplitter PyInstaller Build")
    print("=" * 50)

    clean_old_build()

    if not build_exe():
        print("[ERROR] Build failed - Exiting.")
        return

    if not copy_models_to_dist():
        print("[WARN] Models folder copy failed - Please verify manually.")

    check_file_size()

    print("=" * 50)
    print("[INFO] Build finished successfully.")
    print(f"[INFO] Executable: dist/{PROJECT_NAME}/{PROJECT_NAME}.exe")
    print(f"[INFO] Models folder: dist/{PROJECT_NAME}/{MODEL_DIR}/")


if __name__ == "__main__":
    main()
