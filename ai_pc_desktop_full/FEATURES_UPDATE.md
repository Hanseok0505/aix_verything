# 최신 기능 업데이트

## 새로 추가된 기능

### 1. 폴더 선택 대화상자
- **"폴더 선택" 버튼**: Windows 폴더 선택 대화상자를 열어 경로를 선택할 수 있습니다
- 서버 측에서 PowerShell을 사용하여 폴더 선택 대화상자 실행
- 선택한 경로가 자동으로 입력란에 추가됩니다

### 2. 인덱싱된 경로 관리
- **인덱싱된 경로 목록 표시**: 
  - 인덱싱된 모든 루트 경로를 한눈에 확인
  - 각 경로의 파일 수, 청크 수, 인덱싱 시간 표시
- **경로 삭제 기능**:
  - ✕ 버튼으로 인덱싱된 경로 삭제
  - 삭제 시 해당 경로의 모든 파일, 청크, 벡터 데이터 제거
  - DB와 FAISS 모두에서 완전히 삭제

### 3. Ollama 통합
- **Ollama 설치 스크립트**: `scripts/install_ollama.bat`
- **Ollama 서버 시작**: `scripts/start_ollama.bat`
- **자동 모델 다운로드**: 설치 시 모델 선택 및 다운로드
- **설정 가이드**: `.env` 파일 설정 방법 포함

### 4. 데이터베이스 개선
- **indexed_roots 테이블**: 인덱싱된 루트 경로 추적
- **root_path 컬럼**: 각 파일에 루트 경로 정보 저장
- 경로별 통계 정보 제공

## 사용 방법

### 폴더 선택
1. "폴더 선택" 버튼 클릭
2. Windows 폴더 선택 대화상자에서 폴더 선택
3. 선택한 경로가 자동으로 입력란에 추가됨
4. 여러 경로를 선택하려면 반복하거나 세미콜론으로 구분

### 인덱싱된 경로 관리
- 페이지 로드 시 자동으로 인덱싱된 경로 목록 표시
- 각 경로 옆의 ✕ 버튼으로 삭제
- 삭제 확인 후 DB와 FAISS에서 완전히 제거

### Ollama 설정
1. **설치**:
   ```batch
   scripts\install_ollama.bat
   ```

2. **서버 시작**:
   ```batch
   scripts\start_ollama.bat
   ```

3. **.env 설정**:
   ```
   AI_PC_MODE=internal
   INTERNAL_BASE_URL=http://127.0.0.1:11434/v1
   INTERNAL_API_KEY=ollama
   INTERNAL_MODEL=llama3.2
   ```

## API 엔드포인트

### GET /indexed-roots
인덱싱된 루트 경로 목록 가져오기
```json
{
  "roots": [
    {
      "root_path": "C:\\Users\\me\\Documents",
      "indexed_at": 1234567890,
      "file_count": 100,
      "chunk_count": 500
    }
  ]
}
```

### POST /delete-path
인덱싱된 경로 삭제
```json
// 요청
{
  "root_path": "C:\\Users\\me\\Documents"
}

// 응답
{
  "deleted": true,
  "root_path": "C:\\Users\\me\\Documents",
  "deleted_files": 100,
  "deleted_chunks": 500,
  "deleted_vectors": 500
}
```

### GET /select-folder
Windows 폴더 선택 대화상자 열기
```json
// 응답
{
  "path": "C:\\Users\\me\\Documents"
}
// 또는 취소 시
{
  "path": null,
  "cancelled": true
}
```

## 주의사항

### FAISS 삭제
- 경로 삭제 시 FAISS에서도 벡터가 제거됩니다
- 하지만 FAISS 인덱스는 완전히 재구성되지 않을 수 있습니다
- 완전한 정리를 위해서는 전체 재인덱싱을 권장합니다

### Ollama 서버
- Ollama 서버는 별도 창에서 실행해야 합니다
- 서버가 실행 중이어야 Chat 기능이 작동합니다
- 기본 포트: 11434

## 문제 해결

### 폴더 선택이 작동하지 않을 때
- Windows에서만 사용 가능합니다
- PowerShell 실행 정책 확인 필요할 수 있습니다

### 경로 삭제 후 검색 결과에 여전히 나타날 때
- 브라우저 새로고침
- 서버 재시작
- 전체 재인덱싱 권장

### Ollama 연결 실패
- Ollama 서버가 실행 중인지 확인: `ollama list`
- 포트 11434가 사용 가능한지 확인
- 방화벽 설정 확인


