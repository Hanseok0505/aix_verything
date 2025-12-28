# 빠른 시작 가이드

## ✅ 설치 완료 확인

다음 명령어로 설치가 완료되었는지 확인하세요:

```batch
conda activate ai_pc
python -c "from app.server import app; print('설치 완료!')"
```

## 🚀 실행 방법

### 방법 1: 배치 파일 사용 (가장 간단)

**웹 UI:**
```batch
start_web.bat
```

**데스크톱 앱:**
```batch
start_desktop.bat
```

### 방법 2: 직접 실행

```batch
conda activate ai_pc
python run_web.py
```

브라우저에서 http://127.0.0.1:8000/ui 접속

## 📝 첫 사용 전 설정

### 1. .env 파일 확인

`.env` 파일이 있는지 확인하고, 없으면:
```batch
copy env_example.txt .env
```

### 2. 모드 선택

**내부 Proxy API 사용 (권장):**
```
AI_PC_MODE=internal
INTERNAL_BASE_URL=http://127.0.0.1:4000/v1
INTERNAL_API_KEY=your-key
```

**로컬 LLM 사용:**
```
AI_PC_MODE=local
LOCAL_GGUF_PATH=./models/model.gguf
```

로컬 모델이 없으면:
```batch
conda activate ai_pc
python scripts/download_model.py
```

### 3. 폴더 인덱싱

1. 웹 UI 또는 데스크톱 앱 실행
2. "Index Folder" 패널에서 폴더 경로 입력
3. "Index" 버튼 클릭

또는 CLI:
```batch
conda activate ai_pc
python cli_index.py --root "C:\Users\YourName\Documents"
```

## 💡 사용 예시

### 질문 예시:
- "프로젝트 계획서 파일 찾아줘"
- "최근에 수정한 엑셀 파일 보여줘"
- "Python 코드에서 데이터베이스 연결 부분 찾아줘"
- "분석 결과 문서 열어줘"

### 검색 결과에서:
- **파일 선택 열기**: Windows Explorer에서 파일 선택
- **폴더 열기**: 파일이 있는 폴더 열기

## 🔧 문제 해결

### 가상환경이 인식되지 않을 때
`start_web.bat` 또는 `start_desktop.bat`에서 Python 경로를 확인하세요:
```batch
set PYTHON_EXE=C:\Users\hs\.conda\envs\ai_pc\python.exe
```

실제 경로가 다르면 수정하세요.

### 모델을 찾을 수 없다는 오류
- `.env` 파일에서 `LOCAL_GGUF_PATH` 확인
- 모델 파일이 실제로 존재하는지 확인
- `scripts/download_model.py`로 모델 다운로드

### 서버가 시작되지 않을 때
포트 8000이 이미 사용 중일 수 있습니다. `.env`에서 `PORT=8001`로 변경하세요.

## 📚 더 자세한 정보

- `SETUP_KO.md`: 상세한 설치 및 사용 가이드
- `README.md`: 프로젝트 개요 및 기술 스택


