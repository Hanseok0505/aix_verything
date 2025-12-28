@echo off
chcp 65001 >nul
title AI PC - Start All Services
color 0A

cd /d "%~dp0\.."

echo ========================================
echo AI PC 전체 서비스 시작
echo ========================================
echo.

REM .env 파일 확인
if not exist .env (
    echo .env 파일이 없습니다. 설정이 필요합니다.
    call scripts\quick_setup_llm.bat
    if %ERRORLEVEL% NEQ 0 (
        exit /b 1
    )
)

REM 설정 읽기
for /f "tokens=2 delims==" %%a in ('findstr /i "AI_PC_MODE" .env') do set MODE=%%a
for /f "tokens=2 delims==" %%a in ('findstr /i "INTERNAL_BASE_URL" .env') do set API_URL=%%a

echo 현재 설정:
echo   모드: %MODE%
echo   API URL: %API_URL%
echo.

REM Ollama 모드인 경우 Ollama 서버 시작
if "%MODE%"=="internal" (
    echo %API_URL% | findstr "11434" >nul
    if %ERRORLEVEL% EQU 0 (
        echo [1/2] Ollama 서버 확인...
        curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Ollama 서버를 시작합니다...
            start /B "" cmd /c "title Ollama Server && color 0B && echo Ollama Server && echo API: http://127.0.0.1:11434/v1 && echo. && ollama serve"
            timeout /t 3 /nobreak >nul
            echo Ollama 서버 시작 완료
        ) else (
            echo Ollama 서버가 이미 실행 중입니다.
        )
        echo.
    )
)

REM AI PC 서버 시작
echo [2/2] AI PC 서버 시작...
start cmd /k "start_server_utf8.bat"

echo.
echo ========================================
echo 모든 서비스가 시작되었습니다!
echo ========================================
echo.
echo AI PC 서버: http://127.0.0.1:8000/ui
if "%MODE%"=="internal" (
    echo Ollama 서버: http://127.0.0.1:11434/v1
)
echo.
echo 각 서버는 별도 창에서 실행됩니다.
echo 종료하려면 각 창에서 Ctrl+C를 누르세요.
echo.
pause


