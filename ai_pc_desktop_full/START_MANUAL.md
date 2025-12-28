# AI PC 시작 매뉴얼

## 🚀 빠른 시작

### 1. 서버 시작

**방법 1: 배치 파일 사용 (권장)**
```batch
cd C:\Users\hs\aix_verything\ai_pc_desktop_full
start_web.bat
```

**방법 2: Python 직접 실행**
```batch
cd C:\Users\hs\aix_verything\ai_pc_desktop_full
C:\Users\hs\.conda\envs\ai_pc\python.exe run_web.py
```

**방법 3: PowerShell에서 실행**
```powershell
cd C:\Users\hs\aix_verything\ai_pc_desktop_full
C:\Users\hs\.conda\envs\ai_pc\python.exe run_web.py
```

### 2. 웹 브라우저 접속

서버가 시작되면 브라우저에서 다음 주소를 열어주세요:
```
http://127.0.0.1:8000/ui
```

---

## 📁 파일 인덱싱

### 인덱싱 방법

1. **웹 UI에서 인덱싱**
   - 브라우저에서 `http://127.0.0.1:8000/ui` 접속
   - "1) Index Folder" 섹션에서 경로 입력
   - 여러 경로는 세미콜론(;)으로 구분: `D:\폴더1;D:\폴더2`
   - "Index" 버튼 클릭

2. **폴더 선택 버튼 사용**
   - "폴더 선택" 버튼 클릭
   - 파일 탐색기에서 폴더 선택
   - 자동으로 경로가 추가됨

3. **CLI에서 인덱싱**
   ```batch
   cd C:\Users\hs\aix_verything\ai_pc_desktop_full
   C:\Users\hs\.conda\envs\ai_pc\python.exe cli_index.py --root "D:\인덱싱할폴더"
   ```

### 인덱싱 설정

- **전체 파일 인덱싱**: `.env` 파일에서 `INDEX_EXTS=*` (기본값)
- **특정 확장자만**: `INDEX_EXTS=.txt,.md,.pdf,.docx,.xlsx,.msg`

### 인덱싱된 경로 관리

- **경로 삭제**: 인덱싱된 경로 목록에서 ✕ 버튼 클릭
- **재인덱싱**: 같은 경로를 다시 인덱싱하면 자동으로 기존 데이터 삭제 후 재인덱싱

---

## 💬 Chat / Search 사용법

### Chat 기능

1. **검색어 입력**
   - "2) Chat / Search" 섹션의 입력 필드에 질문 입력
   - 예: "2025 수입 예상치 알려줘", "CV 파일 찾아줘"

2. **Chat 버튼 클릭**
   - LLM이 검색 결과를 기반으로 답변 생성
   - 관련 파일 경로와 내용 요약 제공

3. **Search Only 버튼 클릭**
   - 검색 결과만 표시 (LLM 답변 없음)
   - 파일 경로와 내용 스니펫만 보여줌

### 검색 기능

- **파일명/경로 검색**: 파일 이름이나 경로에 포함된 키워드 검색
- **내용 검색**: 파일 내용에 포함된 텍스트 검색
- **한국어 검색**: 한국어 검색어도 정상 작동

---

## ⚙️ 설정

### .env 파일 설정

현재 설정 위치: `C:\Users\hs\aix_verything\ai_pc_desktop_full\.env`

**주요 설정 항목:**

```env
# LLM 모드 설정
AI_PC_MODE=internal  # internal (Ollama) 또는 local (llama.cpp)

# Ollama 설정 (AI_PC_MODE=internal일 때)
INTERNAL_BASE_URL=http://127.0.0.1:11434/v1
INTERNAL_API_KEY=ollama
INTERNAL_MODEL=llama3.2

# 인덱싱 설정
INDEX_EXTS=*  # 전체 파일 인덱싱 (*) 또는 특정 확장자 (.txt,.pdf 등)

# 임베딩 설정 (RAG 의미 검색)
ENABLE_EMBEDDINGS=false  # true로 설정 시 의미 기반 검색 활성화
```

---

## 🔧 문제 해결

### 서버가 시작되지 않을 때

1. **Python 경로 확인**
   ```batch
   C:\Users\hs\.conda\envs\ai_pc\python.exe --version
   ```

2. **포트 충돌 확인**
   ```batch
   netstat -ano | findstr ":8000"
   ```

3. **의존성 설치 확인**
   ```batch
   cd C:\Users\hs\aix_verything\ai_pc_desktop_full
   C:\Users\hs\.conda\envs\ai_pc\python.exe -m pip install -r requirements.txt
   ```

### 인덱싱이 안 될 때

1. **경로 확인**: 경로가 올바른지 확인 (예: `D:\` 대신 `D:/` 또는 `D:\`)
2. **권한 확인**: 폴더 접근 권한 확인
3. **서버 로그 확인**: 서버 콘솔 창에서 오류 메시지 확인

### Chat이 "No matching files found"만 나올 때

1. **인덱싱 확인**: 파일이 실제로 인덱싱되었는지 확인
2. **검색어 확인**: 다른 검색어로 시도
3. **서버 로그 확인**: 검색 결과가 있는지 서버 콘솔에서 확인

---

## 📝 주요 명령어 요약

### 서버 시작
```batch
cd C:\Users\hs\aix_verything\ai_pc_desktop_full
start_web.bat
```

### 서버 종료
- 서버 창에서 `Ctrl+C` 누르기
- 또는 작업 관리자에서 Python 프로세스 종료

### Ollama 확인
```batch
ollama list
ollama --version
```

### 데이터베이스 확인
```batch
cd C:\Users\hs\aix_verything\ai_pc_desktop_full
C:\Users\hs\.conda\envs\ai_pc\python.exe -c "from app.db import get_conn; conn = get_conn(); cur = conn.execute('SELECT COUNT(*) FROM files'); print(f'파일: {cur.fetchone()[0]}'); cur = conn.execute('SELECT COUNT(*) FROM chunks'); print(f'청크: {cur.fetchone()[0]}'); conn.close()"
```

---

## 🌐 접속 주소

- **웹 UI**: http://127.0.0.1:8000/ui
- **API 문서**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

---

## 📌 현재 설정 상태

- **LLM 모드**: `internal` (Ollama)
- **Ollama URL**: `http://127.0.0.1:11434/v1`
- **모델**: `llama3.2`
- **인덱싱 모드**: 전체 파일 (`INDEX_EXTS=*`)
- **Outlook 파일 지원**: 활성화 (`.msg` 파일 추출 가능)

---

## 💡 사용 팁

1. **인덱싱은 시간이 걸릴 수 있습니다**: 많은 파일이 있는 폴더는 인덱싱에 시간이 소요됩니다.

2. **검색어는 구체적으로**: "2025 수입" 같은 구체적인 검색어가 더 좋은 결과를 제공합니다.

3. **여러 경로 인덱싱**: 세미콜론(;)으로 구분하여 여러 경로를 한 번에 인덱싱할 수 있습니다.

4. **서버 로그 확인**: 문제가 발생하면 서버 콘솔 창의 로그를 확인하세요.

