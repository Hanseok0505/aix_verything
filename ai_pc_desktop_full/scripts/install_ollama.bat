@echo off
echo ========================================
echo Ollama 설치 및 설정
echo ========================================
echo.

REM Ollama가 이미 설치되어 있는지 확인
where ollama >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [확인] Ollama가 이미 설치되어 있습니다.
    ollama --version
    echo.
    goto :setup
)

echo [1/3] Ollama 다운로드 및 설치...
echo Windows용 Ollama는 다음에서 다운로드하세요:
echo https://ollama.com/download/windows
echo.
echo 또는 PowerShell로 설치:
echo   winget install Ollama.Ollama
echo.
set /p INSTALLED="Ollama를 설치하셨나요? (y/N): "
if /i not "%INSTALLED%"=="y" (
    echo 설치를 취소했습니다.
    pause
    exit /b 0
)

:setup
echo.
echo [2/3] Ollama 서비스 시작 확인...
ollama serve >nul 2>&1 &
timeout /t 2 /nobreak >nul

echo.
echo [3/3] 모델 다운로드...
echo 사용할 모델을 선택하세요:
echo 1. llama3.2 (3B) - 가벼움, 빠름
echo 2. llama3.1 (8B) - 균형잡힌 성능
echo 3. qwen2.5 (7B) - 한국어 지원 좋음
echo 4. 직접 입력
echo.
set /p CHOICE="선택 (1-4): "

if "%CHOICE%"=="1" (
    set MODEL=llama3.2
) else if "%CHOICE%"=="2" (
    set MODEL=llama3.1:8b
) else if "%CHOICE%"=="3" (
    set MODEL=qwen2.5:7b
) else if "%CHOICE%"=="4" (
    set /p MODEL="모델 이름 입력 (예: llama3.2): "
) else (
    set MODEL=llama3.2
)

echo.
echo 모델 다운로드 중: %MODEL%
echo (이 작업은 시간이 걸릴 수 있습니다)
ollama pull %MODEL%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 설치 완료!
    echo ========================================
    echo.
    echo 모델: %MODEL%
    echo.
    echo .env 파일에 다음을 추가하세요:
    echo AI_PC_MODE=internal
    echo INTERNAL_BASE_URL=http://127.0.0.1:11434/v1
    echo INTERNAL_API_KEY=ollama
    echo INTERNAL_MODEL=%MODEL%
    echo.
    echo Ollama 서버 시작:
    echo   ollama serve
    echo.
) else (
    echo.
    echo 모델 다운로드 실패
    echo 수동으로 다운로드: ollama pull %MODEL%
)

pause


