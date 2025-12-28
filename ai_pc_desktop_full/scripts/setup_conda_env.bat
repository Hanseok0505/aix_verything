@echo off
echo ========================================
echo AI PC 아나콘다 가상환경 설정
echo ========================================
echo.

REM 아나콘다가 설치되어 있는지 확인
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 오류: 아나콘다가 설치되어 있지 않거나 PATH에 추가되지 않았습니다.
    echo 아나콘다를 설치하거나 PATH를 설정해주세요.
    pause
    exit /b 1
)

REM 현재 디렉토리로 이동
cd /d "%~dp0\.."

REM 가상환경 이름
set ENV_NAME=ai_pc

echo 1. 기존 가상환경 확인...
conda env list | findstr /C:"%ENV_NAME%" >nul
if %ERRORLEVEL% EQU 0 (
    echo 기존 가상환경 '%ENV_NAME%'이 존재합니다.
    set /p OVERWRITE="덮어쓰시겠습니까? (y/N): "
    if /i "%OVERWRITE%"=="y" (
        echo 기존 가상환경 삭제 중...
        conda env remove -n %ENV_NAME% -y
    ) else (
        echo 취소되었습니다.
        pause
        exit /b 0
    )
)

echo.
echo 2. 새 가상환경 생성 중 (Python 3.10)...
conda create -n %ENV_NAME% python=3.10 -y
if %ERRORLEVEL% NEQ 0 (
    echo 오류: 가상환경 생성 실패
    pause
    exit /b 1
)

echo.
echo 3. 가상환경 활성화 중...
call conda activate %ENV_NAME%

echo.
echo 4. pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 5. 필요한 라이브러리 설치 중...
echo (이 작업은 시간이 걸릴 수 있습니다)
pip install -r requirements.txt

echo.
echo 6. sentence-transformers 모델 다운로드 (선택사항)...
echo 모델은 첫 실행 시 자동으로 다운로드됩니다.

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 가상환경 활성화 방법:
echo   conda activate %ENV_NAME%
echo.
echo 실행 방법:
echo   python run_web.py        (웹 UI)
echo   python run_desktop.py    (데스크톱 앱)
echo.
pause

