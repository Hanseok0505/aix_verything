@echo off
chcp 65001 >nul
title Ollama Setup and Start
color 0B

cd /d "%~dp0\.."

echo ========================================
echo Ollama 자동 설정 및 시작
echo ========================================
echo.

REM Ollama 설치 확인
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/4] Ollama 설치 확인...
    echo Ollama가 설치되어 있지 않습니다.
    echo.
    echo 설치 방법:
    echo 1. https://ollama.com/download/windows 에서 다운로드
    echo 2. 또는: winget install Ollama.Ollama
    echo.
    set /p INSTALLED="Ollama를 설치하셨나요? (y/N): "
    if /i not "%INSTALLED%"=="y" (
        echo 설치를 취소했습니다.
        pause
        exit /b 1
    )
    
    REM 다시 확인
    where ollama >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama를 찾을 수 없습니다. PATH를 확인하거나 재시작하세요.
        pause
        exit /b 1
    )
)

echo [1/4] Ollama 확인 완료
ollama --version
echo.

REM Ollama 서버가 이미 실행 중인지 확인
echo [2/4] Ollama 서버 상태 확인...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Ollama 서버가 이미 실행 중입니다.
    goto :check_model
)

REM Ollama 서버 시작
echo Ollama 서버를 시작합니다...
start /B "" cmd /c "title Ollama Server && color 0B && echo Ollama Server Running... && echo API: http://127.0.0.1:11434/v1 && echo. && ollama serve"
timeout /t 3 /nobreak >nul

:check_model
echo [3/4] 모델 확인...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama 서버 연결 실패. 잠시 후 다시 시도합니다...
    timeout /t 5 /nobreak >nul
    curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama 서버를 시작할 수 없습니다.
        pause
        exit /b 1
    )
)

REM 설치된 모델 확인
for /f "tokens=*" %%i in ('ollama list 2^>nul') do (
    echo %%i | findstr /i "llama qwen" >nul
    if !ERRORLEVEL! EQU 0 (
        set HAS_MODEL=1
    )
)

if not defined HAS_MODEL (
    echo 설치된 모델이 없습니다.
    echo.
    echo 모델을 다운로드합니다...
    echo 추천: llama3.2 (가벼움, 빠름)
    echo.
    set /p MODEL="모델 이름 입력 (기본: llama3.2): "
    if "!MODEL!"=="" set MODEL=llama3.2
    
    echo.
    echo 모델 다운로드 중: !MODEL!
    echo (시간이 걸릴 수 있습니다...)
    ollama pull !MODEL!
    
    if %ERRORLEVEL% NEQ 0 (
        echo 모델 다운로드 실패
        pause
        exit /b 1
    )
    
    set SELECTED_MODEL=!MODEL!
) else (
    echo 설치된 모델을 찾았습니다.
    echo 사용할 모델을 선택하세요:
    ollama list
    echo.
    set /p SELECTED_MODEL="모델 이름 입력 (기본: llama3.2): "
    if "!SELECTED_MODEL!"=="" set SELECTED_MODEL=llama3.2
)

echo.
echo [4/4] .env 파일 설정...
if not exist .env (
    if exist env_example.txt (
        copy env_example.txt .env >nul
    )
)

REM .env 파일 업데이트
powershell -Command "$content = Get-Content .env -Raw; $content = $content -replace 'AI_PC_MODE=.*', 'AI_PC_MODE=internal'; $content = $content -replace 'INTERNAL_BASE_URL=.*', 'INTERNAL_BASE_URL=http://127.0.0.1:11434/v1'; $content = $content -replace 'INTERNAL_API_KEY=.*', 'INTERNAL_API_KEY=ollama'; $content = $content -replace 'INTERNAL_MODEL=.*', 'INTERNAL_MODEL=%SELECTED_MODEL%'; Set-Content .env -Value $content -NoNewline"

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 모델: %SELECTED_MODEL%
echo API URL: http://127.0.0.1:11434/v1
echo.
echo .env 파일이 업데이트되었습니다.
echo 서버를 재시작하면 Chat 기능을 사용할 수 있습니다.
echo.
pause


