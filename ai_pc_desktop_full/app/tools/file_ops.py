import os, subprocess, sys

def open_in_explorer(path: str) -> bool:
    path = os.path.abspath(path)
    try:
        if sys.platform.startswith("win"):
            if os.path.isfile(path):
                subprocess.Popen(["explorer.exe", "/select,", path])
            else:
                subprocess.Popen(["explorer.exe", path])
            return True
        if sys.platform == "darwin":
            if os.path.isfile(path):
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["open", path])
            return True
        subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False
