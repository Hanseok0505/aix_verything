"""Chat 기능 테스트 스크립트"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.config import settings
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.local_stub import LocalStubProvider
from app.providers.local_llamacpp import LocalLlamaCppProvider

print("=" * 60)
print("Chat 기능 테스트")
print("=" * 60)
print(f"\n현재 모드: {settings.mode}")
print(f"Internal URL: {settings.internal_base_url}")
print(f"Internal Model: {settings.internal_model}")
print(f"Local Model Path: {settings.local_gguf_path}")

print("\n" + "=" * 60)
print("프로바이더 테스트")
print("=" * 60)

if settings.mode == "internal":
    print("\n[내부 API 모드]")
    try:
        provider = OpenAICompatibleProvider()
        print("[OK] 프로바이더 초기화 성공")
        
        # 간단한 테스트
        print("\n테스트 메시지 전송 중...")
        response = provider.chat([{"role": "user", "content": "Hello"}])
        print(f"[OK] 응답 수신: {response[:100]}...")
    except Exception as e:
        print(f"[ERROR] 오류: {e}")
        print("\n해결 방법:")
        print("1. 내부 API 서버가 실행 중인지 확인")
        print(f"2. URL 확인: {settings.internal_base_url}")
        print("3. 또는 .env에서 AI_PC_MODE=local로 변경")

elif settings.mode == "local":
    print("\n[로컬 LLM 모드]")
    try:
        provider = LocalLlamaCppProvider()
        print("[OK] 프로바이더 초기화 성공")
        
        # 간단한 테스트
        print("\n테스트 메시지 전송 중...")
        response = provider.chat([{"role": "user", "content": "Hello"}])
        print(f"[OK] 응답 수신: {response[:100]}...")
    except FileNotFoundError as e:
        print(f"[ERROR] 모델 파일을 찾을 수 없음: {e}")
        print("\n해결 방법:")
        print("1. 모델 다운로드: python scripts/download_model.py")
        print(f"2. .env에서 LOCAL_GGUF_PATH 확인: {settings.local_gguf_path}")
    except Exception as e:
        print(f"[ERROR] 오류: {e}")
else:
    print("\n[Stub 모드]")
    provider = LocalStubProvider()
    print("[WARNING] LLM이 설정되지 않았습니다.")
    print("Chat 기능을 사용하려면:")
    print("1. .env에서 AI_PC_MODE=internal 또는 local로 설정")
    print("2. 해당 모드에 맞는 설정 완료")

print("\n" + "=" * 60)

