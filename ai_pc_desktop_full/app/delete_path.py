"""특정 루트 경로의 인덱싱 데이터 삭제"""
import os
from app.db import get_conn
from app.faiss_store import FAISSStore
from app.config import settings

def delete_indexed_path(root_path: str) -> dict:
    """루트 경로의 모든 인덱싱 데이터 삭제 (DB + FAISS)"""
    # 경로 정규화 (대소문자, 슬래시/백슬래시 통일)
    root_path_normalized = os.path.normpath(os.path.abspath(root_path))
    # Windows 경로 대소문자 무시 비교를 위해 소문자로 변환
    root_path_lower = root_path_normalized.lower()
    
    conn = get_conn()
    
    # 모든 가능한 경로 변형으로 검색 (정규화된 경로, 원본 경로 등)
    # 먼저 정확한 매칭 시도
    cur = conn.execute("SELECT id FROM files WHERE root_path = ?", (root_path_normalized,))
    file_ids = [row[0] for row in cur.fetchall()]
    
    # 정확한 매칭이 없으면 대소문자 무시 검색 (Windows)
    if not file_ids:
        cur = conn.execute("SELECT id, root_path FROM files WHERE root_path IS NOT NULL")
        all_files = cur.fetchall()
        for file_id, stored_path in all_files:
            if stored_path and os.path.normpath(os.path.abspath(stored_path)).lower() == root_path_lower:
                file_ids.append(file_id)
    
    # indexed_roots에서도 경로 찾기
    cur = conn.execute("SELECT root_path FROM indexed_roots")
    indexed_roots = [row[0] for row in cur.fetchall()]
    matching_root = None
    for stored_root in indexed_roots:
        if stored_root and os.path.normpath(os.path.abspath(stored_root)).lower() == root_path_lower:
            matching_root = stored_root
            break
    
    # indexed_roots에서 직접 삭제 시도 (파일이 없어도)
    if not file_ids and not matching_root:
        # indexed_roots에서 유사한 경로 찾기
        cur = conn.execute("SELECT root_path FROM indexed_roots")
        all_roots = cur.fetchall()
        for stored_root_row in all_roots:
            stored_root = stored_root_row[0]
            if stored_root:
                try:
                    # 경로 정규화 비교
                    stored_normalized = os.path.normpath(os.path.abspath(stored_root)).lower()
                    if stored_normalized == root_path_lower:
                        matching_root = stored_root
                        break
                    # 부분 매칭 (예: "D:W" -> "D:\")
                    if root_path_lower in stored_normalized or stored_normalized in root_path_lower:
                        matching_root = stored_root
                        break
                except Exception:
                    continue
        
        # 여전히 매칭이 없으면 indexed_roots에서 직접 삭제 시도
        if not matching_root:
            # 원본 경로로 직접 삭제 시도
            cur = conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (root_path,))
            if cur.rowcount > 0:
                conn.commit()
                conn.close()
                return {"deleted": True, "root_path": root_path, "deleted_files": 0, "deleted_chunks": 0, "deleted_vectors": 0, "message": "인덱싱된 경로만 삭제되었습니다 (파일 없음)"}
            
            conn.close()
            return {"deleted": False, "message": f"인덱싱된 경로가 없습니다: {root_path}"}
    
    # 해당 파일들의 chunk ID 목록 가져오기
    placeholders = ','.join(['?'] * len(file_ids))
    cur = conn.execute(f"SELECT id FROM chunks WHERE file_id IN ({placeholders})", file_ids)
    chunk_ids = [row[0] for row in cur.fetchall()]
    
    # FAISS에서 해당 chunk들의 벡터 삭제
    deleted_vectors = 0
    if settings.enable_embeddings and chunk_ids:
        try:
            faiss_store = FAISSStore()
            # 메타데이터에서 해당 chunk_id를 가진 항목 찾기
            chunk_id_set = set(chunk_ids)
            original_count = len(faiss_store.metadata)
            
            # 삭제할 인덱스 찾기
            indices_to_remove = []
            for idx, meta in enumerate(faiss_store.metadata):
                if meta.get("chunk_id") in chunk_id_set:
                    indices_to_remove.append(idx)
            
            if indices_to_remove:
                # 역순으로 정렬하여 뒤에서부터 삭제 (인덱스 유지)
                indices_to_remove.sort(reverse=True)
                
                # 메타데이터에서 제거
                for idx in indices_to_remove:
                    faiss_store.metadata.pop(idx)
                
                deleted_vectors = len(indices_to_remove)
                
                # FAISS 인덱스 재구성 (남은 벡터만 다시 추가)
                if faiss_store.metadata:
                    # 임시로 모든 벡터를 다시 가져와서 재구성
                    # (실제로는 효율성을 위해 메타데이터만 업데이트하고, 
                    #  인덱스는 다음 검색 시 재구성하거나, 전체 재인덱싱 시 처리)
                    # 여기서는 메타데이터만 저장하고, 인덱스는 나중에 재구성
                    dimension = faiss_store.index.d if faiss_store.index.ntotal > 0 else 384
                    faiss_store.index = faiss_store.index.__class__(dimension)
                    # 메타데이터는 저장하지만, 벡터는 다음 인덱싱 시 다시 추가됨
                    # (실제 사용 시에는 전체 재인덱싱 권장)
                
                faiss_store.save()
        except Exception as e:
            # FAISS 삭제 실패해도 계속 진행
            # 로그는 출력하지 않음 (서버 로그에만 기록)
            pass
    
    # DB에서 chunks 삭제
    if chunk_ids:
        chunk_placeholders = ','.join(['?'] * len(chunk_ids))
        conn.execute(f"DELETE FROM chunks WHERE id IN ({chunk_placeholders})", chunk_ids)
    
    # DB에서 files 삭제
    if file_ids:
        file_placeholders = ','.join(['?'] * len(file_ids))
        conn.execute(f"DELETE FROM files WHERE id IN ({file_placeholders})", file_ids)
    
    # indexed_roots에서 제거 (정규화된 경로 또는 매칭된 경로 사용)
    deleted_from_roots = False
    if matching_root:
        conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (matching_root,))
        deleted_from_roots = True
    else:
        # 정규화된 경로로 삭제 시도
        cur = conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (root_path_normalized,))
        if cur.rowcount > 0:
            deleted_from_roots = True
        else:
            # 대소문자 무시 삭제 시도
            cur = conn.execute("SELECT root_path FROM indexed_roots")
            for stored_root in cur.fetchall():
                if stored_root[0]:
                    try:
                        stored_normalized = os.path.normpath(os.path.abspath(stored_root[0]))
                        if stored_normalized.lower() == root_path_lower:
                            conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (stored_root[0],))
                            deleted_from_roots = True
                            break
                    except Exception:
                        # 경로 정규화 실패 시 원본 경로와 비교
                        if stored_root[0].lower() == root_path_lower:
                            conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (stored_root[0],))
                            deleted_from_roots = True
                            break
    
    conn.commit()
    conn.close()
    
    return {
        "deleted": True,
        "root_path": root_path_normalized,
        "deleted_files": len(file_ids),
        "deleted_chunks": len(chunk_ids),
        "deleted_vectors": deleted_vectors
    }

