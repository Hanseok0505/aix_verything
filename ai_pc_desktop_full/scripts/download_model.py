"""
로컬 LLM 모델 다운로드 스크립트
저사양 PC용 가벼운 모델을 다운로드합니다.
"""
import os
import sys
import requests
from pathlib import Path

# 추천 모델 목록 (저사양 PC용)
MODELS = {
    "tinyllama-1.1b": {
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "size_mb": 736,
        "description": "가장 가벼운 모델 (1.1B 파라미터, Q4_K_M 양자화)"
    },
    "phi-2": {
        "url": "https://huggingface.co/microsoft/phi-2/resolve/main/phi-2.gguf",
        "size_mb": 1600,
        "description": "Microsoft Phi-2 (2.7B 파라미터)"
    },
    "qwen2-0.5b": {
        "url": "https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0.5b-instruct-q4_k_m.gguf",
        "size_mb": 400,
        "description": "Qwen2 0.5B (가장 가벼운 옵션)"
    }
}

def download_file(url: str, filepath: Path, chunk_size: int = 8192):
    """파일 다운로드 (진행률 표시)"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    downloaded = 0
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r다운로드 중... {percent:.1f}% ({downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB)", end='')
    print("\n다운로드 완료!")

def main():
    print("=" * 60)
    print("로컬 LLM 모델 다운로드")
    print("=" * 60)
    print("\n사용 가능한 모델:")
    for i, (key, info) in enumerate(MODELS.items(), 1):
        print(f"{i}. {key} - {info['description']} ({info['size_mb']}MB)")
    
    choice = input("\n다운로드할 모델 번호를 선택하세요 (1-3): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(MODELS):
            print("잘못된 선택입니다.")
            return
        model_key = list(MODELS.keys())[idx]
        model_info = MODELS[model_key]
    except ValueError:
        print("숫자를 입력해주세요.")
        return
    
    # 모델 저장 경로
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    
    # 파일명 추출
    filename = model_info['url'].split('/')[-1]
    filepath = models_dir / filename
    
    if filepath.exists():
        print(f"\n모델 파일이 이미 존재합니다: {filepath}")
        overwrite = input("덮어쓰시겠습니까? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("취소되었습니다.")
            return
    
    print(f"\n모델: {model_key}")
    print(f"크기: {model_info['size_mb']}MB")
    print(f"저장 위치: {filepath}")
    print(f"\n다운로드를 시작합니다...")
    
    try:
        download_file(model_info['url'], filepath)
        print(f"\n모델이 성공적으로 다운로드되었습니다!")
        print(f"경로: {filepath.absolute()}")
        print(f"\n.env 파일에서 다음 설정을 추가하세요:")
        print(f"LOCAL_GGUF_PATH={filepath}")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("requests 라이브러리가 필요합니다. 설치 중...")
        os.system(f"{sys.executable} -m pip install requests")
        import requests
    
    main()

