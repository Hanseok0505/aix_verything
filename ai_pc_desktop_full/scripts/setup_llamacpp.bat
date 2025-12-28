@echo off
chcp 65001 >nul
title llama.cpp Setup
color 0C

cd /d "%~dp0\.."

echo ========================================
echo llama.cpp 모드 설정
echo ========================================
echo.

echo [1/3] 모델 다운로드...
if not exist models (
    mkdir models
)

echo 모델을 다운로드합니다.
python scripts\download_model.py

if %ERRORLEVEL% NEQ 0 (
    echo 모델 다운로드 실패
    pause
    exit /b 1
)

echo.
echo [2/3] 다운로드한 모델 확인...
dir /b models\*.gguf 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 모델 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo.
echo [3/3] .env 파일 설정...
if not exist .env (
    if exist env_example.txt (
        copy env_example.txt .env >nul
    )
)

REM 다운로드한 첫 번째 모델 사용
for %%f in (models\*.gguf) do (
    set MODEL_PATH=%%f
    goto :found
)

:found
echo 모델 경로: %MODEL_PATH%

REM .env 파일 업데이트
powershell -Command "$content = Get-Content .env -Raw; $content = $content -replace 'AI_PC_MODE=.*', 'AI_PC_MODE=local'; $content = $content -replace 'LOCAL_GGUF_PATH=.*', 'LOCAL_GGUF_PATH=%MODEL_PATH%'; Set-Content .env -Value $content -NoNewline"

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 모드: local (llama.cpp)
echo 모델: %MODEL_PATH%
echo.
echo 서버를 재시작하면 Chat 기능을 사용할 수 있습니다.
echo.
pause


