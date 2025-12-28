@echo off
:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [경고] 관리자 권한이 없습니다. 일부 기능이 제한될 수 있습니다.
    echo.
)

echo ========================================
echo AI PC 전체 기능 테스트
echo ========================================
echo.

cd /d "%~dp0"

REM 아나콘다 가상환경
set CONDA_ENV=ai_pc
set PYTHON_EXE=C:\Users\hs\.conda\envs\%CONDA_ENV%\python.exe

if not exist "%PYTHON_EXE%" (
    echo [오류] 가상환경을 찾을 수 없습니다: %PYTHON_EXE%
    pause
    exit /b 1
)

echo [테스트 1/7] Python 버전 확인...
"%PYTHON_EXE%" --version
if %errorLevel% neq 0 (
    echo [실패] Python 실행 실패
    pause
    exit /b 1
)
echo [성공] Python 정상
echo.

echo [테스트 2/7] 필수 모듈 import 테스트...
"%PYTHON_EXE%" -c "import fastapi; import uvicorn; import faiss; import sentence_transformers; print('  ✓ 모든 필수 모듈 로드 성공')" 2>nul
if %errorLevel% neq 0 (
    echo [실패] 필수 모듈 import 실패
    pause
    exit /b 1
)
echo [성공] 필수 모듈 정상
echo.

echo [테스트 3/7] 애플리케이션 모듈 import 테스트...
"%PYTHON_EXE%" -c "from app.config import settings; from app.db import init_db; from app.server import app; from app.indexer import index_folder; from app.search import search_files; from app.rag import search_rag; print('  ✓ 애플리케이션 모듈 로드 성공')" 2>nul
if %errorLevel% neq 0 (
    echo [실패] 애플리케이션 모듈 import 실패
    pause
    exit /b 1
)
echo [성공] 애플리케이션 모듈 정상
echo.

echo [테스트 4/7] 데이터베이스 초기화...
"%PYTHON_EXE%" -c "from app.db import init_db; init_db(); print('  ✓ DB 초기화 완료')" 2>nul
if %errorLevel% neq 0 (
    echo [경고] DB 초기화 실패 (계속 진행)
) else (
    echo [성공] DB 초기화 완료
)
echo.

echo [테스트 5/7] 서버 시작 테스트...
start /B "" "%PYTHON_EXE%" run_web.py
timeout /t 4 /nobreak >nul

REM Health check
powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -Method Get -TimeoutSec 3; Write-Host '[성공] 서버 실행 중 - Mode:' $r.mode } catch { Write-Host '[실패] 서버 응답 없음:' $_.Exception.Message }" 2>nul
if %errorLevel% neq 0 (
    echo [경고] Health check 실패 (서버가 아직 시작 중일 수 있음)
)
echo.

echo [테스트 6/7] API 엔드포인트 테스트...
powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/search' -Method Post -Body (@{message='test'} | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec 3; Write-Host '[성공] 검색 API 정상' } catch { Write-Host '[경고] 검색 API 테스트 실패' }" 2>nul

powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/ui' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host '[성공] UI 페이지 접근 가능' } } catch { Write-Host '[경고] UI 접근 실패' }" 2>nul
echo.

echo [테스트 7/7] 파일 열기 기능 테스트...
if exist "%USERPROFILE%\Documents" (
    "%PYTHON_EXE%" -c "from app.tools.file_ops import open_in_explorer; import os; test_path = os.path.expanduser('~\\Documents'); result = open_in_explorer(test_path); print('  ✓ 파일 열기 기능 테스트 완료 (결과:', result, ')')" 2>nul
    if %errorLevel% equ 0 (
        echo [성공] 파일 열기 기능 정상
    ) else (
        echo [경고] 파일 열기 기능 테스트 실패
    )
) else (
    echo [건너뜀] 테스트 디렉토리 없음
)
echo.

echo ========================================
echo 테스트 완료
echo ========================================
echo.
echo 서버가 실행 중입니다:
echo   - 웹 UI: http://127.0.0.1:8000/ui
echo   - Health: http://127.0.0.1:8000/health
echo.
echo 서버를 종료하려면:
echo   - 작업 관리자에서 python.exe 프로세스 종료
echo   - 또는 Ctrl+C (터미널에서 실행한 경우)
echo.
pause


