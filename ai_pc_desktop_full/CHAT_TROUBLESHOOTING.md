# Chat 기능 문제 해결 가이드

## Chat이 동작하지 않는 경우

### 1. 내부 API 서버 확인 (AI_PC_MODE=internal)

**문제**: 내부 Proxy API 서버가 실행 중이지 않음

**해결 방법**:
1. 내부 API 서버가 실행 중인지 확인:
   ```powershell
   # API 서버 상태 확인
   Invoke-WebRequest -Uri "http://127.0.0.1:4000/v1/models" -UseBasicParsing
   ```

2. `.env` 파일에서 설정 확인:
   ```
   INTERNAL_BASE_URL=http://127.0.0.1:4000/v1
   INTERNAL_API_KEY=your-api-key
   INTERNAL_MODEL=your-model-name
   ```

3. 내부 API 서버를 실행하거나, 올바른 URL로 변경

### 2. 로컬 LLM 사용 (AI_PC_MODE=local)

**문제**: 로컬 모델 파일이 없음

**해결 방법**:
1. `.env` 파일에서 모드 변경:
   ```
   AI_PC_MODE=local
   LOCAL_GGUF_PATH=./models/model.gguf
   ```

2. 모델 다운로드:
   ```batch
   conda activate ai_pc
   python scripts/download_model.py
   ```

3. 다운로드한 모델 경로를 `.env`에 설정

### 3. 오류 메시지 확인

Chat 실행 시 오류 메시지가 표시되면:
- **"LLM 프로바이더 초기화 실패"**: 설정 파일 확인
- **"LLM 호출 실패"**: API 서버 연결 또는 모델 파일 확인
- **"내부 API 서버가 실행 중인지 확인"**: API 서버 시작 필요

### 4. 빠른 테스트

**내부 API 모드 테스트**:
```python
from app.providers.openai_compatible import OpenAICompatibleProvider
provider = OpenAICompatibleProvider()
response = provider.chat([{"role": "user", "content": "Hello"}])
print(response)
```

**로컬 모드 테스트**:
```python
from app.providers.local_llamacpp import LocalLlamaCppProvider
provider = LocalLlamaCppProvider()
response = provider.chat([{"role": "user", "content": "Hello"}])
print(response)
```

## 현재 설정 확인

```batch
conda activate ai_pc
python -c "from app.config import settings; print('Mode:', settings.mode); print('Internal URL:', settings.internal_base_url); print('Local Model:', settings.local_gguf_path)"
```

## 권장 설정

### 옵션 1: 내부 API 사용 (권장)
```
AI_PC_MODE=internal
INTERNAL_BASE_URL=http://your-api-server/v1
INTERNAL_API_KEY=your-key
INTERNAL_MODEL=your-model
```

### 옵션 2: 로컬 LLM 사용
```
AI_PC_MODE=local
LOCAL_GGUF_PATH=./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
LOCAL_CTX=4096
LOCAL_THREADS=8
```


