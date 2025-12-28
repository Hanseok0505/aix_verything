@echo off
chcp 65001 >nul
title LLM Quick Setup
color 0E

cd /d "%~dp0\.."

echo ========================================
echo LLM 빠른 설정
echo ========================================
echo.
echo 사용할 LLM을 선택하세요:
echo.
echo 1. Ollama (권장) - 설치 및 설정 자동화
echo 2. llama.cpp - 로컬 모델 파일 사용
echo 3. 현재 설정 확인
echo.
set /p CHOICE="선택 (1-3): "

if "%CHOICE%"=="1" (
    call scripts\setup_and_start_ollama.bat
) else if "%CHOICE%"=="2" (
    call scripts\setup_llamacpp.bat
) else if "%CHOICE%"=="3" (
    echo.
    echo 현재 설정:
    echo.
    if exist .env (
        findstr /i "AI_PC_MODE INTERNAL_BASE_URL INTERNAL_MODEL LOCAL_GGUF_PATH" .env
    ) else (
        echo .env 파일이 없습니다.
    )
    echo.
    pause
) else (
    echo 잘못된 선택입니다.
    pause
    exit /b 1
)


