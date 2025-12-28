# 한글 인코딩 문제 해결

## 수정 사항

### 1. 배치 파일 인코딩 설정
- `chcp 65001`: UTF-8 코드페이지 설정
- `PYTHONIOENCODING=utf-8`: Python 입출력 인코딩
- `PYTHONUTF8=1`: Python 3.7+ UTF-8 모드 활성화

### 2. Python 스크립트 인코딩 설정
- `run_web.py`: stdout/stderr UTF-8 래퍼 추가
- `run_desktop.py`: 동일한 인코딩 설정

### 3. 서버 시작 스크립트
- `start_server_window.bat`: UTF-8 설정 포함
- `start_server_utf8.bat`: 전용 UTF-8 버전

## 사용 방법

### 권장: UTF-8 버전 사용
```batch
start_server_utf8.bat
```

### 또는 기존 스크립트 사용
```batch
start_server_window.bat
```

두 스크립트 모두 UTF-8 인코딩이 설정되어 있습니다.

## 문제 해결

### 여전히 한글이 깨질 때
1. 콘솔 폰트 확인: Consolas 또는 다른 유니코드 폰트 사용
2. Windows 지역 설정 확인
3. Python 버전 확인 (3.7 이상 권장)

### Ctrl+C가 작동하지 않을 때
- 작업 관리자에서 python.exe 프로세스 강제 종료
- 또는 명령 창을 닫기

## 참고

- Windows 콘솔의 기본 인코딩은 CP949 (한국어)
- UTF-8로 변경하면 모든 유니코드 문자 정상 표시
- 일부 오래된 프로그램은 여전히 CP949를 사용할 수 있음


