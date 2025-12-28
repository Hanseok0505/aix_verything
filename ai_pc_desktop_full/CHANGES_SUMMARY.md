# 변경 사항 요약

## 완료된 개선 사항

### 1. ✅ 폴더 선택 UI 개선
- **변경 전**: 텍스트 입력만 가능
- **변경 후**: 
  - 여러 경로를 세미콜론(;)으로 구분하여 입력 가능
  - textarea로 변경하여 여러 줄 입력 지원
  - "경로 추가" 버튼 추가
  - 인덱싱 결과 상세 표시 (파일 수, 청크 수, 벡터 수)

### 2. ✅ 여러 폴더 인덱싱 지원
- **서버 API 수정**: `/index` 엔드포인트가 여러 경로를 받을 수 있도록 수정
- **형식**: 세미콜론(;) 또는 줄바꿈으로 구분
- **예시**: 
  ```
  C:\Users\me\Documents;D:\Projects;E:\Work
  ```
- **결과**: 각 경로별 인덱싱 결과와 전체 요약 제공

### 3. ✅ Chat 결과에 Chunk 내용 표시
- **변경 전**: 파일 경로만 표시
- **변경 후**:
  - 파일 검색 결과
  - 키워드 매칭 chunk 내용 (최대 300자 미리보기)
  - 의미 매칭 chunk 내용 (RAG 활성화 시)
  - 각 결과에 "Open" 버튼 제공
  - 결과를 카테고리별로 구분하여 표시

### 4. ✅ Chat 동작 문제 해결
- **오류 처리 개선**: 
  - 프로바이더 초기화 실패 시 명확한 오류 메시지
  - LLM 호출 실패 시 상세한 오류 정보 제공
  - 내부 API 모드: API 서버 연결 상태 확인 안내
  - 로컬 모드: 모델 파일 경로 확인 안내
- **테스트 스크립트 추가**: `test_chat.py`로 Chat 기능 테스트 가능

**현재 상태**: 
- 모드: `internal` (내부 API 사용)
- 내부 API 서버가 실행 중이지 않음
- **해결 방법**:
  1. 내부 API 서버 실행, 또는
  2. `.env`에서 `AI_PC_MODE=local`로 변경 후 모델 다운로드

### 5. ✅ Search 부분 문자열 매칭 지원
- **변경 전**: FTS5 정확한 단어 매칭만 지원
- **변경 후**:
  - FTS5 검색 (정확한 단어 매칭)
  - LIKE 검색 (부분 문자열 매칭) 추가
  - 두 검색 결과를 결합하여 더 많은 결과 제공
  - `search_files()`와 `search_chunks()` 모두 개선

## UI 개선 사항

### 인덱싱 섹션
- textarea로 변경 (여러 경로 입력 가능)
- "경로 추가" 버튼
- 인덱싱 진행 상태 및 결과 상세 표시

### 검색/채팅 섹션
- Chat 결과에 chunk 내용 표시
- 결과를 카테고리별로 구분 (파일, 키워드 매칭, 의미 매칭)
- 각 chunk에 미리보기 제공
- 오류 메시지 개선 (해결 방법 안내 포함)

## API 변경 사항

### `/index` 엔드포인트
```json
// 요청
{
  "root": "C:\\path1;D:\\path2;E:\\path3"
}

// 응답
{
  "results": [
    {"root": "C:\\path1", "indexed_files": 10, ...},
    {"root": "D:\\path2", "indexed_files": 5, ...}
  ],
  "summary": {
    "total_roots": 3,
    "total_files": 15,
    "total_chunks": 120,
    "total_vectors": 120
  }
}
```

### `/chat` 엔드포인트
- 응답에 `snippets`와 `rag_snippets` 포함 (chunk 내용)
- 오류 발생 시 `error` 필드에 상세 정보 제공

## 사용 방법

### 여러 폴더 인덱싱
```
C:\Users\me\Documents;D:\Projects;E:\Work
```

또는 여러 줄:
```
C:\Users\me\Documents
D:\Projects
E:\Work
```

### Chat 사용
1. 질문 입력
2. "Chat" 버튼 클릭
3. 결과 확인:
   - LLM 답변
   - 파일 검색 결과
   - Chunk 내용 (키워드 매칭)
   - Chunk 내용 (의미 매칭, RAG 활성화 시)

### Search 사용
- 부분 문자열도 검색됨
- 예: "계약서" 검색 시 "계약서파일", "계약서_최종" 등도 찾음

## 문제 해결

### Chat이 동작하지 않을 때
1. `test_chat.py` 실행하여 문제 확인:
   ```batch
   conda activate ai_pc
   python test_chat.py
   ```

2. 내부 API 모드인 경우:
   - API 서버 실행 확인
   - `.env`의 `INTERNAL_BASE_URL` 확인

3. 로컬 모드로 전환:
   ```env
   AI_PC_MODE=local
   LOCAL_GGUF_PATH=./models/model.gguf
   ```
   모델 다운로드: `python scripts/download_model.py`

## 추가 파일

- `test_chat.py`: Chat 기능 테스트 스크립트
- `CHAT_TROUBLESHOOTING.md`: Chat 문제 해결 가이드


