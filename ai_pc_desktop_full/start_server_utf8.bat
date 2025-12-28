@echo off
REM UTF-8 인코딩 설정
chcp 65001 >nul
title AI PC Server
color 0A

cd /d "%~dp0"

REM 환경 변수 설정
set PYTHON_EXE=C:\Users\hs\.conda\envs\ai_pc\python.exe
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ========================================
echo AI PC Server
echo ========================================
echo.
echo Virtual Environment: ai_pc
echo Python: %PYTHON_EXE%
echo.
echo Starting server...
echo Open http://127.0.0.1:8000/ui in browser
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found: %PYTHON_EXE%
    pause
    exit /b 1
)

REM Python 실행 (Ctrl+C 처리 개선)
"%PYTHON_EXE%" run_web.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server stopped with error code: %ERRORLEVEL%
    pause
)


