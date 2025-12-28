# AI PC (Local File RAG) — Web UI / Desktop App

저사양 PC에서 GPU 없이 동작하는 개인용 AI 파일 검색 및 질의응답 시스템입니다.

## 주요 기능
- **파일 인덱싱**: SQLite (메타데이터 + FTS) 및 FAISS (선택적 임베딩)
- **다중 검색 방식**:
  - 파일명/경로 키워드 검색 (SQLite FTS)
  - 문서 내용 키워드 검색 (SQLite FTS)
  - 의미 기반 검색 (RAG, FAISS 임베딩)
- **LLM 통합**:
  - **내부 Proxy API** (OpenAI 호환, 권장)
  - **로컬 LLM** (llama.cpp 기반, CPU 전용)
- **파일 열기**: Windows Explorer에서 파일/폴더 직접 열기

## 시스템 요구사항
- Windows 10/11
- 아나콘다 또는 Miniconda
- 최소 4GB RAM (로컬 LLM 사용 시 8GB 권장)
- GPU 불필요 (CPU만으로 동작)

---

## 빠른 시작

### 1) 아나콘다 가상환경 생성 및 라이브러리 설치

**Windows:**
```batch
scripts\setup_conda_env.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/setup_conda_env.sh
./scripts/setup_conda_env.sh
```

또는 수동으로:
```bash
conda create -n ai_pc python=3.10 -y
conda activate ai_pc
pip install -r requirements.txt
```

### 2) 설정 파일 생성

`env_example.txt`를 `.env`로 복사하고 필요한 값 수정:
```batch
copy env_example.txt .env
```

주요 설정:
- `AI_PC_MODE`: `internal` (내부 API) 또는 `local` (로컬 LLM)
- `ENABLE_EMBEDDINGS`: `true`로 설정 시 RAG 의미 검색 활성화
- `INTERNAL_BASE_URL`: 내부 Proxy API 주소 (internal 모드)
- `LOCAL_GGUF_PATH`: 로컬 모델 경로 (local 모드)

### 3) 로컬 LLM 모델 다운로드 (선택사항, local 모드 사용 시)

```bash
conda activate ai_pc
python scripts/download_model.py
```

### 4) 실행

**웹 UI:**
```batch
start_web.bat
```
또는
```bash
conda activate ai_pc
python run_web.py
```
브라우저에서 http://127.0.0.1:8000/ui 열기

**데스크톱 앱:**
```batch
start_desktop.bat
```
또는
```bash
conda activate ai_pc
python run_desktop.py
```

### 5) 폴더 인덱싱

UI의 "Index Folder" 패널 사용 또는 CLI:
```bash
conda activate ai_pc
python cli_index.py --root "C:\your\folder"
```

---

## Build executables (Windows)
We include a build script using PyInstaller. Run in PowerShell:
```powershell
./scripts/build_windows.ps1
```
Outputs go to `dist/`.

## Build executables (macOS/Linux)
```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile run_web.py --name ai-pc-web
pyinstaller --noconfirm --clean --onefile run_desktop.py --name ai-pc-desktop
```

> Note: the sandbox build attached here is **Linux**. For Windows EXE, run the build script on Windows.
