import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    mode: str = os.getenv("AI_PC_MODE", "internal")

    data_dir: str = os.getenv("DATA_DIR", "./data")
    sqlite_path: str = os.getenv("SQLITE_PATH", "./data/meta.db")

    index_exts: str = os.getenv("INDEX_EXTS", "*")  # 기본값: 전체 파일 인덱싱
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    enable_embeddings: bool = os.getenv("ENABLE_EMBEDDINGS", "false").lower() in ("1","true","yes","y")
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    faiss_dir: str = os.getenv("FAISS_DIR", "./data/faiss")

    internal_base_url: str = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:4000/v1")
    internal_api_key: str = os.getenv("INTERNAL_API_KEY", "dummy-key")
    internal_model: str = os.getenv("INTERNAL_MODEL", "internal-llm-chat")
    
    # Proxy를 통한 내부 API (liteproxy -> fabrix LLM)
    use_proxy: bool = os.getenv("USE_PROXY", "false").lower() in ("1","true","yes","y")
    proxy_url: str = os.getenv("PROXY_URL", "http://127.0.0.1:8080/v1")
    proxy_api_key: str = os.getenv("PROXY_API_KEY", "")

    local_gguf_path: str = os.getenv("LOCAL_GGUF_PATH", "./models/model.gguf")
    local_ctx: int = int(os.getenv("LOCAL_CTX", "4096"))
    local_threads: int = int(os.getenv("LOCAL_THREADS", "8"))

    host: str = os.getenv("HOST","127.0.0.1")
    port: int = int(os.getenv("PORT","8000"))

settings = Settings()
