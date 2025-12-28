import os
import pickle
import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional
from app.config import settings

class FAISSStore:
    def __init__(self, index_path: Optional[str] = None):
        if index_path:
            self.index_path = index_path
            self.meta_path = index_path.replace(".faiss", ".meta")
        else:
            self.index_path = os.path.join(settings.faiss_dir, "index.faiss")
            self.meta_path = os.path.join(settings.faiss_dir, "index.meta")
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict] = []  # 각 벡터에 대한 메타데이터 (chunk_id, file_id, path 등)
        self._load()

    def _load(self):
        """기존 인덱스와 메타데이터 로드"""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
            except Exception:
                self.index = None
                self.metadata = []
        if self.index is None:
            # 새 인덱스 생성 (384차원은 all-MiniLM-L6-v2 기준)
            dimension = 384
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """벡터와 메타데이터 추가"""
        if len(vectors) == 0:
            return
        if self.index.ntotal == 0:
            # 첫 추가 시 차원 확인
            if vectors.shape[1] != self.index.d:
                # 차원이 맞지 않으면 재생성
                self.index = faiss.IndexFlatL2(vectors.shape[1])
        vectors_np = np.array(vectors, dtype=np.float32)
        self.index.add(vectors_np)
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[Dict, float]]:
        """유사도 검색 (거리와 메타데이터 반환)"""
        if self.index.ntotal == 0:
            return []
        query_np = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(query_np, min(k, self.index.ntotal))
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distances[0][i])))
        return results

    def save(self):
        """인덱스와 메타데이터 저장"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def clear(self):
        """인덱스 초기화"""
        dimension = 384
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        self.save()

    def get_count(self) -> int:
        """저장된 벡터 개수"""
        return self.index.ntotal if self.index else 0

