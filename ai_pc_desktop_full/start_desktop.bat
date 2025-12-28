@echo off
setlocal
echo ========================================
echo AI PC 데스크톱 앱 시작
echo ========================================
echo.

REM 아나콘다 가상환경 사용
set CONDA_ENV=ai_pc
set PYTHON_EXE=C:\Users\hs\.conda\envs\%CONDA_ENV%\python.exe

REM 가상환경이 존재하는지 확인
if not exist "%PYTHON_EXE%" (
    echo 오류: 아나콘다 가상환경 '%CONDA_ENV%'을 찾을 수 없습니다.
    echo 먼저 scripts\setup_conda_env.bat을 실행하여 가상환경을 생성하세요.
    pause
    exit /b 1
)

echo 가상환경: %CONDA_ENV%
echo Python: %PYTHON_EXE%
echo.

REM .env 파일 확인
if not exist .env (
    if exist env_example.txt (
        echo .env 파일이 없습니다. env_example.txt를 복사합니다...
        copy env_example.txt .env
    ) else (
        echo 경고: .env 파일이 없습니다.
    )
)

echo 서버를 시작합니다...
echo 브라우저에서 http://127.0.0.1:8000/ui 를 열거나 데스크톱 창이 열립니다.
echo.

"%PYTHON_EXE%" run_desktop.py

pause
