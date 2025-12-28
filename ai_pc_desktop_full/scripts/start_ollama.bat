@echo off
title Ollama Server
color 0B
echo ========================================
echo Ollama 서버 시작
echo ========================================
echo.
echo Ollama 서버를 시작합니다...
echo API URL: http://127.0.0.1:11434/v1
echo.
echo 종료하려면 Ctrl+C를 누르거나 이 창을 닫으세요
echo ========================================
echo.

where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Ollama가 설치되어 있지 않습니다.
    echo scripts\install_ollama.bat을 실행하여 설치하세요.
    pause
    exit /b 1
)

ollama serve

pause


