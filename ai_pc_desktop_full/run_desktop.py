import sys
import io
import threading, time
import webview
import uvicorn
from app.server import app
from app.config import settings

# UTF-8 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_server():
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="warning")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(0.8)
    webview.create_window("AI PC", f"http://{settings.host}:{settings.port}/ui", width=1100, height=780)
    webview.start()
