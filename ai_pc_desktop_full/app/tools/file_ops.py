import os, subprocess, sys

def open_in_explorer(path: str) -> bool:
    """파일이 있는 폴더를 열고 파일을 선택합니다."""
    path = os.path.abspath(path)
    try:
        if sys.platform.startswith("win"):
            if os.path.isfile(path):
                # Windows: /select 옵션 사용 (공백 없이 쉼표)
                # 경로에 공백이 있을 수 있으므로 따옴표로 감싸지 않고 직접 전달
                subprocess.Popen(["explorer.exe", "/select,", path], shell=False)
            else:
                subprocess.Popen(["explorer.exe", path], shell=False)
            return True
        if sys.platform == "darwin":
            if os.path.isfile(path):
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["open", path])
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        print(f"[File Ops] Error opening in explorer: {e}")
        return False

def open_file(path: str) -> bool:
    """파일을 기본 애플리케이션으로 직접 엽니다."""
    path = os.path.abspath(path)
    try:
        if sys.platform.startswith("win"):
            # Windows: os.startfile 사용 (가장 안정적)
            os.startfile(path)
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        print(f"[File Ops] Error opening file: {e}")
        return False
