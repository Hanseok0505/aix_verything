# AI PC 설치 및 사용 가이드 (한국어)

## 개요
저사양 PC에서 GPU 없이 동작하는 개인용 AI 파일 검색 시스템입니다. 내 PC의 파일을 RAG로 연결하여 LLM으로 질문하고 찾을 수 있으며, 찾은 파일의 위치로 바로 이동할 수 있습니다.

## 설치 단계

### 1단계: 아나콘다 가상환경 생성

**Windows:**
```batch
cd ai_pc_desktop_full
scripts\setup_conda_env.bat
```

이 스크립트는:
- Python 3.10 가상환경 생성 (`ai_pc`)
- 필요한 모든 라이브러리 설치
- sentence-transformers 모델 준비

**수동 설치:**
```bash
conda create -n ai_pc python=3.10 -y
conda activate ai_pc
pip install -r requirements.txt
```

### 2단계: 설정 파일 생성

```batch
copy env_example.txt .env
```

`.env` 파일을 열어 다음 설정을 확인/수정:

#### 모드 선택
- **내부 Proxy API 사용** (권장):
  ```
  AI_PC_MODE=internal
  INTERNAL_BASE_URL=http://127.0.0.1:4000/v1
  INTERNAL_API_KEY=your-api-key
  INTERNAL_MODEL=your-model-name
  ```

- **로컬 LLM 사용**:
  ```
  AI_PC_MODE=local
  LOCAL_GGUF_PATH=./models/model.gguf
  LOCAL_CTX=4096
  LOCAL_THREADS=8
  ```

#### RAG 의미 검색 활성화 (선택사항)
```
ENABLE_EMBEDDINGS=true
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 3단계: 로컬 LLM 모델 다운로드 (local 모드만)

```bash
conda activate ai_pc
python scripts/download_model.py
```

추천 모델:
- **TinyLlama 1.1B** (736MB): 가장 가벼움, 저사양 PC용
- **Qwen2 0.5B** (400MB): 초경량 옵션
- **Phi-2** (1.6GB): 더 나은 성능

### 4단계: 실행

**웹 UI:**
```batch
start_web.bat
```
브라우저에서 http://127.0.0.1:8000/ui 접속

**데스크톱 앱:**
```batch
start_desktop.bat
```

## 사용 방법

### 1. 폴더 인덱싱

1. UI의 "Index Folder" 패널에서 폴더 경로 입력
2. "Index" 버튼 클릭
3. 인덱싱 진행 상황 확인

또는 CLI:
```bash
conda activate ai_pc
python cli_index.py --root "C:\Users\YourName\Documents"
```

### 2. 파일 검색 및 질문

**예시 질문:**
- "프로젝트 계획서 파일 찾아줘"
- "최근에 수정한 엑셀 파일 보여줘"
- "Python 코드에서 데이터베이스 연결 부분 찾아줘"

### 3. 파일 열기

검색 결과에서:
- **파일 선택 열기**: 파일을 Windows Explorer에서 선택된 상태로 열기
- **폴더 열기**: 파일이 있는 폴더 열기

## 주요 기능

### 검색 방식

1. **키워드 검색** (항상 활성화)
   - 파일명, 경로, 내용에서 키워드 매칭
   - SQLite FTS5 사용

2. **의미 검색** (RAG, 선택적)
   - `ENABLE_EMBEDDINGS=true` 설정 시 활성화
   - sentence-transformers로 임베딩 생성
   - FAISS로 유사도 검색
   - 예: "데이터 분석 결과" → "통계 리포트", "분석 자료" 등 유사 의미 찾기

### LLM 모드

1. **Internal 모드** (권장)
   - 내부 Proxy를 통한 LLM API 사용
   - OpenAI 호환 API 지원
   - 빠른 응답 속도

2. **Local 모드**
   - 로컬 llama.cpp 기반 LLM 실행
   - 완전 오프라인 동작
   - CPU만으로 동작 (GPU 불필요)

## 문제 해결

### 가상환경이 인식되지 않을 때
```batch
conda activate ai_pc
where python
```
Python 경로가 `C:\Users\hs\.conda\envs\ai_pc\python.exe`인지 확인

### 모델을 찾을 수 없다는 오류
- `.env` 파일에서 `LOCAL_GGUF_PATH` 확인
- 모델 파일이 실제로 존재하는지 확인
- `scripts/download_model.py`로 모델 다운로드

### 임베딩 생성이 느릴 때
- `ENABLE_EMBEDDINGS=false`로 설정하여 키워드 검색만 사용
- 인덱싱할 폴더 범위를 줄이기
- `CHUNK_SIZE`를 줄이기 (기본값: 900)

### 메모리 부족 오류
- 로컬 LLM 사용 시 더 작은 모델 선택 (TinyLlama 1.1B)
- `LOCAL_CTX` 값을 줄이기 (기본값: 4096)
- `ENABLE_EMBEDDINGS=false`로 설정

## 배포용 빌드

Windows 실행 파일 생성:
```powershell
conda activate ai_pc
.\scripts\build_windows.ps1
```

생성된 파일: `dist/ai-pc-desktop.exe`, `dist/ai-pc-web.exe`

## 기술 스택

- **백엔드**: FastAPI
- **데이터베이스**: SQLite (FTS5)
- **벡터 스토어**: FAISS
- **임베딩**: sentence-transformers
- **로컬 LLM**: llama.cpp (llama-cpp-python)
- **UI**: HTML/JavaScript (웹), pywebview (데스크톱)

## 라이선스

이 프로젝트는 개인 사용 및 배포를 목적으로 합니다.


