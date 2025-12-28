@echo off
chcp 65001 >nul
title LLM Setup Now
color 0E

cd /d "%~dp0\.."

echo ========================================
echo LLM 즉시 설정
echo ========================================
echo.
echo Chat 기능을 사용하려면 LLM이 필요합니다.
echo.
echo 선택지:
echo 1. Ollama 설치 및 설정 (권장, 쉬움)
echo 2. llama.cpp 모드 (로컬 모델 파일, 더 가벼움)
echo.
set /p CHOICE="선택 (1 또는 2): "

if "%CHOICE%"=="1" (
    echo.
    echo Ollama 설치를 시작합니다...
    call scripts\install_ollama_auto.bat
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Ollama 설정을 완료합니다...
        call scripts\auto_setup_ollama.bat
    )
) else if "%CHOICE%"=="2" (
    echo.
    echo llama.cpp 모드로 설정합니다...
    echo.
    echo 사용할 모델을 선택하세요:
    echo 1. tinyllama-1.1b (736MB) - 가장 가벼움
    echo 2. qwen2-0.5b (400MB) - 초경량
    echo 3. phi-2 (1600MB) - 균형잡힌 성능
    echo.
    set /p MODEL_CHOICE="모델 선택 (1-3, 기본: 1): "
    
    if "%MODEL_CHOICE%"=="1" (
        set MODEL_URL=https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
        set MODEL_NAME=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
    ) else if "%MODEL_CHOICE%"=="2" (
        set MODEL_URL=https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf
        set MODEL_NAME=qwen2-0.5b-instruct-q4_k_m.gguf
    ) else if "%MODEL_CHOICE%"=="3" (
        set MODEL_URL=https://huggingface.co/microsoft/phi-2/resolve/main/phi-2.gguf
        set MODEL_NAME=phi-2.gguf
    ) else (
        set MODEL_URL=https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
        set MODEL_NAME=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
    )
    
    echo.
    echo 모델 다운로드 중: %MODEL_NAME%
    echo (시간이 걸릴 수 있습니다...)
    echo.
    
    if not exist models mkdir models
    
    REM Python으로 다운로드
    python -c "import requests; import os; url='%MODEL_URL%'; path=os.path.join('models', '%MODEL_NAME%'); print(f'Downloading {url}...'); r=requests.get(url, stream=True); total=int(r.headers.get('content-length',0)); downloaded=0; f=open(path,'wb'); [f.write(chunk) or (downloaded:=downloaded+len(chunk)) or print(f'\rProgress: {downloaded*100//total if total>0 else 0}%%', end='') for chunk in r.iter_content(chunk_size=8192)]; f.close(); print(f'\nDownloaded: {path}')"
    
    if exist "models\%MODEL_NAME%" (
        echo 모델 다운로드 완료!
        echo.
        echo .env 파일 설정 중...
        
        if not exist .env (
            if exist env_example.txt copy env_example.txt .env >nul
        )
        
        powershell -Command "$content = Get-Content .env -Raw -Encoding UTF8; $content = $content -replace '(?m)^AI_PC_MODE=.*$', 'AI_PC_MODE=local'; $content = $content -replace '(?m)^LOCAL_GGUF_PATH=.*$', 'LOCAL_GGUF_PATH=./models/%MODEL_NAME%'; [System.IO.File]::WriteAllText((Resolve-Path .env), $content, [System.Text.Encoding]::UTF8)"
        
        echo.
        echo ========================================
        echo 설정 완료!
        echo ========================================
        echo.
        echo 모드: local (llama.cpp)
        echo 모델: models\%MODEL_NAME%
        echo.
        echo 서버를 재시작하면 Chat 기능을 사용할 수 있습니다.
    ) else (
        echo 모델 다운로드 실패
        echo 수동으로 다운로드하거나 Ollama를 사용하세요.
    )
) else (
    echo 잘못된 선택입니다.
)

echo.
pause


