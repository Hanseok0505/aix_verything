import sys
import io
import uvicorn
from app.config import settings
from app.server import app

# UTF-8 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port, 
        log_level="info",
        log_config=None  # 기본 로그 설정 사용
    )
