import os, time
import numpy as np
from typing import Iterable, Dict, Any, List
from app.config import settings
from app.db import get_conn
from app.extractors import extract_text
from app.chunker import chunk_text
from app.embeddings import embed_texts
from app.faiss_store import FAISSStore

def _iter_files(root: str, exts: List[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        # skip common heavy dirs
        dirnames[:] = [d for d in dirnames if d not in (".git","node_modules","__pycache__")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in exts:
                yield p

def index_folder(root: str) -> Dict[str, Any]:
    root = os.path.abspath(root)  # 정규화된 경로 사용
    exts = [e.strip().lower() for e in settings.index_exts.split(",") if e.strip()]
    conn = get_conn()
    indexed_files=0
    indexed_chunks=0
    skipped=0
    indexed_vectors=0
    
    # indexed_roots 테이블에 루트 경로 기록
    conn.execute("""
        INSERT OR REPLACE INTO indexed_roots(root_path, indexed_at, file_count, chunk_count)
        VALUES (?, ?, 0, 0)
    """, (root, int(time.time())))
    
    # FAISS 스토어 초기화 (임베딩 활성화 시)
    faiss_store = None
    if settings.enable_embeddings:
        faiss_store = FAISSStore()
        # 기존 벡터 초기화 (전체 재인덱싱 시)
        # faiss_store.clear()  # 필요시 주석 해제
    
    batch_chunks = []
    batch_metadata = []
    
    for path in _iter_files(root, exts):
        try:
            st = os.stat(path)
            name=os.path.basename(path)
            ext=os.path.splitext(name)[1].lower()
            size=int(st.st_size)
            mtime=int(st.st_mtime)

            cur = conn.execute("SELECT id, mtime FROM files WHERE path=?;", (path,))
            row = cur.fetchone()
            if row and int(row[1]) == mtime:
                skipped += 1
                continue

            if row:
                file_id=row[0]
                conn.execute("UPDATE files SET name=?, ext=?, size=?, mtime=? WHERE id=?;", (name,ext,size,mtime,file_id))
                # remove old chunks
                conn.execute("DELETE FROM chunks WHERE file_id=?;", (file_id,))
            else:
                conn.execute("INSERT OR IGNORE INTO files(path,name,ext,size,mtime,root_path) VALUES (?,?,?,?,?,?);",
                             (path,name,ext,size,mtime,root))
                file_id = conn.execute("SELECT id FROM files WHERE path=?;", (path,)).fetchone()[0]

            indexed_files += 1

            text = extract_text(path)
            if not text:
                continue
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
            
            # chunks를 DB에 저장
            chunk_ids = []
            for idx, ch in enumerate(chunks):
                cur = conn.execute("INSERT INTO chunks(file_id, chunk_index, text) VALUES (?,?,?);",
                             (file_id, idx, ch))
                chunk_id = cur.lastrowid
                chunk_ids.append(chunk_id)
            
            indexed_chunks += len(chunks)
            
            # 임베딩 생성 및 FAISS 저장 (배치 처리)
            if settings.enable_embeddings and faiss_store and chunks:
                try:
                    embeddings = embed_texts(chunks)
                    for chunk_id, embedding in zip(chunk_ids, embeddings):
                        batch_chunks.append(embedding)
                        batch_metadata.append({
                            "chunk_id": chunk_id,
                            "file_id": file_id,
                            "path": path
                        })
                    indexed_vectors += len(chunks)
                except Exception as e:
                    # 임베딩 실패 시 스킵
                    pass

            # 배치로 FAISS에 추가 (100개마다)
            if len(batch_chunks) >= 100 and faiss_store:
                try:
                    vectors_np = np.array(batch_chunks, dtype=np.float32)
                    faiss_store.add_vectors(vectors_np, batch_metadata)
                    batch_chunks = []
                    batch_metadata = []
                except Exception:
                    pass

            if indexed_files % 25 == 0:
                conn.commit()
        except Exception:
            continue

    # 남은 배치 처리
    if batch_chunks and faiss_store:
        try:
            vectors_np = np.array(batch_chunks, dtype=np.float32)
            faiss_store.add_vectors(vectors_np, batch_metadata)
            faiss_store.save()
        except Exception:
            pass

    # indexed_roots 업데이트
    conn.execute("""
        UPDATE indexed_roots 
        SET file_count = ?, chunk_count = ?
        WHERE root_path = ?
    """, (indexed_files, indexed_chunks, root))
    
    conn.commit()
    conn.close()
    
    if faiss_store:
        faiss_store.save()
    
    return {
        "indexed_files": indexed_files, 
        "indexed_chunks": indexed_chunks, 
        "indexed_vectors": indexed_vectors if settings.enable_embeddings else 0,
        "skipped": skipped,
        "root": root
    }
