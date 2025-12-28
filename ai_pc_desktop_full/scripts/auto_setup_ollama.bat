@echo off
chcp 65001 >nul
title Auto Setup Ollama
color 0B

cd /d "%~dp0\.."

echo ========================================
echo Ollama 자동 설정
echo ========================================
echo.

REM 1. Ollama 설치 확인
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Ollama가 설치되어 있지 않습니다.
    echo.
    echo 설치 방법:
    echo 1. https://ollama.com/download/windows
    echo 2. 또는: winget install Ollama.Ollama
    echo.
    echo 설치 후 이 스크립트를 다시 실행하세요.
    pause
    exit /b 1
)

echo [1/4] Ollama 확인 완료
ollama --version
echo.

REM 2. Ollama 서버 시작
echo [2/4] Ollama 서버 시작...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama 서버를 시작합니다...
    start /B "" cmd /c "title Ollama Server && color 0B && echo Ollama Server && echo API: http://127.0.0.1:11434/v1 && echo Press Ctrl+C to stop && echo. && ollama serve"
    timeout /t 5 /nobreak >nul
    
    REM 서버 시작 확인
    curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama 서버 시작 실패. 잠시 후 다시 시도합니다...
        timeout /t 5 /nobreak >nul
        curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Ollama 서버를 시작할 수 없습니다.
            pause
            exit /b 1
        )
    )
    echo Ollama 서버 시작 완료
) else (
    echo Ollama 서버가 이미 실행 중입니다.
)
echo.

REM 3. 모델 확인 및 다운로드
echo [3/4] 모델 확인...
set MODEL=llama3.2
set HAS_MODEL=0

for /f "tokens=*" %%i in ('ollama list 2^>nul') do (
    echo %%i | findstr /i "llama3.2" >nul
    if !ERRORLEVEL! EQU 0 (
        set HAS_MODEL=1
    )
)

if %HAS_MODEL% EQU 0 (
    echo 모델 %MODEL%이 설치되어 있지 않습니다.
    echo 모델을 다운로드합니다...
    echo (시간이 걸릴 수 있습니다...)
    ollama pull %MODEL%
    
    if %ERRORLEVEL% NEQ 0 (
        echo 모델 다운로드 실패
        pause
        exit /b 1
    )
    echo 모델 다운로드 완료
) else (
    echo 모델 %MODEL%이 이미 설치되어 있습니다.
)
echo.

REM 4. .env 파일 업데이트
echo [4/4] .env 파일 설정...
if not exist .env (
    if exist env_example.txt (
        copy env_example.txt .env >nul
        echo .env 파일을 생성했습니다.
    ) else (
        echo .env 파일을 생성할 수 없습니다.
        pause
        exit /b 1
    )
)

REM PowerShell로 .env 업데이트
powershell -Command "$content = Get-Content .env -Raw -Encoding UTF8; $content = $content -replace '(?m)^AI_PC_MODE=.*$', 'AI_PC_MODE=internal'; $content = $content -replace '(?m)^INTERNAL_BASE_URL=.*$', 'INTERNAL_BASE_URL=http://127.0.0.1:11434/v1'; $content = $content -replace '(?m)^INTERNAL_API_KEY=.*$', 'INTERNAL_API_KEY=ollama'; $content = $content -replace '(?m)^INTERNAL_MODEL=.*$', 'INTERNAL_MODEL=%MODEL%'; [System.IO.File]::WriteAllText((Resolve-Path .env), $content, [System.Text.Encoding]::UTF8)"

echo .env 파일이 업데이트되었습니다.
echo.

echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 모드: internal (Ollama)
echo 모델: %MODEL%
echo API URL: http://127.0.0.1:11434/v1
echo.
echo AI PC 서버를 재시작하면 Chat 기능을 사용할 수 있습니다.
echo.
pause


