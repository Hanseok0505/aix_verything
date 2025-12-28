@echo off
:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 관리자 권한이 필요합니다. UAC 창에서 승인해주세요.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================
echo AI PC 관리자 모드 실행 및 테스트
echo ========================================
echo.

cd /d "%~dp0"

REM 아나콘다 가상환경 사용
set CONDA_ENV=ai_pc
set PYTHON_EXE=C:\Users\hs\.conda\envs\%CONDA_ENV%\python.exe

REM 가상환경 확인
if not exist "%PYTHON_EXE%" (
    echo [오류] 가상환경을 찾을 수 없습니다: %PYTHON_EXE%
    pause
    exit /b 1
)

echo [1/5] 환경 확인...
echo   - Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

echo [2/5] 모듈 import 테스트...
"%PYTHON_EXE%" -c "from app.config import settings; from app.db import init_db; from app.server import app; print('  ✓ 모든 모듈 로드 성공')" 2>nul
if %errorLevel% neq 0 (
    echo [오류] 모듈 import 실패
    pause
    exit /b 1
)
echo.

echo [3/5] 데이터베이스 초기화...
"%PYTHON_EXE%" -c "from app.db import init_db; init_db(); print('  ✓ DB 초기화 완료')" 2>nul
if %errorLevel% neq 0 (
    echo [경고] DB 초기화 실패 (계속 진행)
)
echo.

echo [4/5] 서버 시작 테스트 (5초간 실행)...
start /B "" "%PYTHON_EXE%" run_web.py
timeout /t 3 /nobreak >nul

echo [5/5] 서버 상태 확인...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 서버가 정상적으로 실행 중입니다!
    echo   ✓ 브라우저에서 http://127.0.0.1:8000/ui 접속 가능
) else (
    echo   ⚠ 서버 응답 확인 실패 (curl이 없거나 서버 시작 중일 수 있음)
)

echo.
echo ========================================
echo 테스트 완료
echo ========================================
echo.
echo 서버를 계속 실행하려면:
echo   - 브라우저에서 http://127.0.0.1:8000/ui 접속
echo   - 종료하려면 Ctrl+C
echo.
pause


