@echo off
chcp 65001 >nul
title Quick Fix Chat
color 0E

cd /d "%~dp0"

echo ========================================
echo Chat 기능 빠른 수정
echo ========================================
echo.
echo Chat 오류를 해결하기 위한 빠른 설정입니다.
echo.
echo 선택지:
echo 1. Ollama 설치 및 설정 (권장)
echo 2. llama.cpp 모드로 전환 (더 빠름, 모델 다운로드 필요)
echo.
set /p CHOICE="선택 (1 또는 2): "

if "%CHOICE%"=="1" (
    echo.
    echo Ollama 설치를 시작합니다...
    call scripts\install_ollama_auto.bat
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Ollama 설정을 완료합니다...
        call scripts\auto_setup_ollama.bat
    )
    echo.
    echo 설정이 완료되었습니다!
    echo 서버를 재시작하세요: start_server_utf8.bat
) else if "%CHOICE%"=="2" (
    echo.
    echo llama.cpp 모드로 전환합니다...
    call scripts\setup_llm_now.bat
    echo.
    echo 설정이 완료되었습니다!
    echo 서버를 재시작하세요: start_server_utf8.bat
) else (
    echo 잘못된 선택입니다.
    pause
    exit /b 1
)

pause


