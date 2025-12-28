@echo off
chcp 65001 >nul
title Install Ollama
color 0B

echo ========================================
echo Ollama 자동 설치
echo ========================================
echo.

REM winget으로 설치 시도
where winget >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [방법 1] winget으로 설치 시도...
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Ollama 설치 완료!
        echo.
        echo PATH를 새로고침합니다...
        call refreshenv >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo 경고: PATH가 자동으로 업데이트되지 않았습니다.
            echo 새 명령 프롬프트 창을 열거나 시스템을 재시작하세요.
        )
        echo.
        echo 설치 확인 중...
        timeout /t 2 /nobreak >nul
        where ollama >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo Ollama 설치 확인 완료!
            ollama --version
            echo.
            echo 이제 scripts\auto_setup_ollama.bat을 실행하세요.
        ) else (
            echo Ollama를 찾을 수 없습니다.
            echo 새 명령 프롬프트 창을 열어주세요.
        )
        pause
        exit /b 0
    )
)

echo.
echo [방법 2] 수동 설치 필요
echo.
echo 1. 다음 URL에서 Ollama를 다운로드하세요:
echo    https://ollama.com/download/windows
echo.
echo 2. 다운로드한 설치 파일을 실행하세요.
echo.
echo 3. 설치 완료 후 이 스크립트를 다시 실행하거나
echo    scripts\auto_setup_ollama.bat을 실행하세요.
echo.
pause


