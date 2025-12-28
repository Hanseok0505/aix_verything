@echo off
echo ========================================
echo 로컬 LLM 설정 가이드
echo ========================================
echo.
echo AI PC는 다음 로컬 LLM을 지원합니다:
echo.
echo 1. Ollama (권장)
echo    - 설치: scripts\install_ollama.bat
echo    - 실행: scripts\start_ollama.bat
echo    - 설정: .env에서 INTERNAL_BASE_URL=http://127.0.0.1:11434/v1
echo.
echo 2. llama.cpp (로컬 모델 파일)
echo    - 모델 다운로드: python scripts\download_model.py
echo    - 설정: .env에서 AI_PC_MODE=local
echo.
echo 3. Open-WebUI (선택사항)
echo    - 별도 설치 필요
echo    - 설정: .env에서 INTERNAL_BASE_URL을 Open-WebUI 주소로
echo.
echo ========================================
echo.
set /p CHOICE="설정할 옵션을 선택하세요 (1-3): "

if "%CHOICE%"=="1" (
    call scripts\install_ollama.bat
) else if "%CHOICE%"=="2" (
    echo.
    echo llama.cpp 모델 다운로드를 시작합니다...
    conda activate ai_pc
    python scripts\download_model.py
) else if "%CHOICE%"=="3" (
    echo.
    echo Open-WebUI는 별도로 설치해야 합니다.
    echo https://github.com/open-webui/open-webui 참고
    echo.
    echo 설치 후 .env에서 다음을 설정:
    echo INTERNAL_BASE_URL=http://127.0.0.1:3000/api/v1
) else (
    echo 잘못된 선택입니다.
)

pause


