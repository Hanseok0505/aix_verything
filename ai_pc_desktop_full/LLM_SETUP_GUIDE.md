# LLM 설정 가이드

## 현재 상황
Chat 기능을 사용하려면 LLM이 필요합니다. 현재 내부 API 서버가 실행 중이지 않아 오류가 발생하고 있습니다.

## 해결 방법

### 방법 1: Ollama 사용 (권장)

#### 1단계: Ollama 설치
```batch
scripts\install_ollama_auto.bat
```
또는 수동 설치:
- https://ollama.com/download/windows 에서 다운로드
- 또는: `winget install Ollama.Ollama`

#### 2단계: Ollama 설정 및 시작
```batch
scripts\auto_setup_ollama.bat
```
이 스크립트는:
- Ollama 서버를 자동으로 시작
- 모델을 다운로드 (llama3.2)
- .env 파일을 자동으로 업데이트

#### 3단계: 서버 재시작
```batch
start_server_utf8.bat
```

### 방법 2: llama.cpp 사용 (로컬 모델)

#### 1단계: 모델 다운로드 및 설정
```batch
scripts\setup_llm_now.bat
```
선택지 2를 선택하면:
- 모델 선택 (tinyllama-1.1b, qwen2-0.5b, phi-2)
- 자동 다운로드
- .env 파일 자동 업데이트

#### 2단계: 서버 재시작
```batch
start_server_utf8.bat
```

## 통합 스크립트

### 모든 서비스 한 번에 시작
```batch
scripts\start_all.bat
```
이 스크립트는:
- Ollama 모드인 경우 Ollama 서버 자동 시작
- AI PC 서버 시작
- 모든 서비스가 별도 창에서 실행

## 설정 확인

### 현재 설정 확인
```batch
type .env | findstr "AI_PC_MODE INTERNAL_BASE_URL INTERNAL_MODEL LOCAL_GGUF_PATH"
```

### Ollama 서버 상태 확인
```powershell
curl http://127.0.0.1:11434/api/tags
```

## 문제 해결

### Ollama 설치 실패
- 관리자 권한으로 실행
- 방화벽 설정 확인
- 수동 설치: https://ollama.com/download/windows

### 모델 다운로드 실패
- 인터넷 연결 확인
- 디스크 공간 확인
- 수동 다운로드: `ollama pull llama3.2`

### Chat 여전히 작동하지 않음
1. 서버 재시작 확인
2. .env 파일 설정 확인
3. LLM 서버 실행 상태 확인

## 권장 설정

### Ollama (권장)
```
AI_PC_MODE=internal
INTERNAL_BASE_URL=http://127.0.0.1:11434/v1
INTERNAL_API_KEY=ollama
INTERNAL_MODEL=llama3.2
```

### llama.cpp
```
AI_PC_MODE=local
LOCAL_GGUF_PATH=./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
LOCAL_CTX=4096
LOCAL_THREADS=8
```

## 빠른 시작

가장 빠른 방법:
```batch
scripts\setup_llm_now.bat
```
선택지 1 (Ollama) 또는 2 (llama.cpp)를 선택하면 자동으로 설정됩니다.


