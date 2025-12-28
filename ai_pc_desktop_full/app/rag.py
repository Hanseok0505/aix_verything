from typing import List, Dict
import numpy as np
from app.config import settings
from app.embeddings import embed_text
from app.faiss_store import FAISSStore
from app.db import get_conn

_faiss_store: FAISSStore = None

def get_faiss_store() -> FAISSStore:
    """싱글톤 FAISS 스토어"""
    global _faiss_store
    if _faiss_store is None:
        _faiss_store = FAISSStore()
    return _faiss_store

def search_rag(query: str, limit: int = 5) -> List[Dict]:
    """RAG 기반 의미 검색"""
    if not settings.enable_embeddings:
        return []
    
    try:
        # 쿼리 임베딩
        query_embedding = embed_text(query)
        query_vector = np.array(query_embedding, dtype=np.float32)
        
        # FAISS 검색
        store = get_faiss_store()
        results = store.search(query_vector, k=limit)
        
        # 메타데이터에서 chunk 정보 가져오기
        conn = get_conn()
        rag_results = []
        for meta, distance in results:
            chunk_id = meta.get("chunk_id")
            if chunk_id:
                cur = conn.execute(
                    """
                    SELECT c.text, c.chunk_index, f.path, f.name
                    FROM chunks c
                    JOIN files f ON f.id = c.file_id
                    WHERE c.id = ?
                    """,
                    (chunk_id,)
                )
                row = cur.fetchone()
                if row:
                    rag_results.append({
                        "text": row[0],
                        "chunk_index": row[1],
                        "path": row[2],
                        "name": row[3],
                        "distance": distance
                    })
        conn.close()
        return rag_results
    except Exception as e:
        # 오류 발생 시 빈 리스트 반환
        return []

