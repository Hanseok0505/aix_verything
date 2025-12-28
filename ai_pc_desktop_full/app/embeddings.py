import os
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.config import settings

_model: Optional[SentenceTransformer] = None

def get_embedder():
    """싱글톤 임베딩 모델 로더"""
    global _model
    if _model is None:
        model_name = settings.embed_model
        cache_dir = os.path.join(settings.data_dir, "models", "sentence-transformers")
        os.makedirs(cache_dir, exist_ok=True)
        _model = SentenceTransformer(model_name, cache_folder=cache_dir)
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    """텍스트 리스트를 임베딩 벡터로 변환"""
    if not texts:
        return []
    model = get_embedder()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()

def embed_text(text: str) -> List[float]:
    """단일 텍스트를 임베딩 벡터로 변환"""
    return embed_texts([text])[0]

