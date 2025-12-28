from typing import List, Dict
from app.db import get_conn

def search_files(query: str, limit: int = 20) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    
    all_results = []
    seen_paths = set()
    
    # 1. LIKE 검색을 우선 사용 (한국어 검색에 더 효과적)
    like_term = f"%{q}%"
    cur = conn.execute(
        """
        SELECT DISTINCT f.path, f.name 
        FROM files f
        WHERE (f.path LIKE ? OR f.name LIKE ?)
        LIMIT ?;
        """,
        (like_term, like_term, limit * 2)  # 더 많이 가져와서 중복 제거
    )
    like_results = cur.fetchall()
    for r in like_results:
        if r[0] not in seen_paths:
            all_results.append(r)
            seen_paths.add(r[0])
            if len(all_results) >= limit:
                break
    
    # 2. FTS5 검색 시도 (추가 결과)
    if len(all_results) < limit:
        try:
            search_term = q.replace('"','').replace("'", "")
            cur = conn.execute(
                "SELECT path, name FROM files_fts WHERE files_fts MATCH ? LIMIT ?;",
                (search_term, limit)
            )
            fts_results = cur.fetchall()
            for r in fts_results:
                if r[0] not in seen_paths:
                    all_results.append(r)
                    seen_paths.add(r[0])
                    if len(all_results) >= limit:
                        break
        except Exception:
            # FTS5 실패 시 무시
            pass
    
    # 3. 단어별 검색 (한국어 검색 개선)
    if len(all_results) < limit:
        words = q.split()
        for word in words:
            if len(word) < 2:  # 너무 짧은 단어는 스킵
                continue
            word_like = f"%{word}%"
            # 이미 본 경로 제외를 위한 쿼리
            if seen_paths:
                placeholders = ','.join(['?'] * min(len(seen_paths), 100))
                cur = conn.execute(
                    f"""
                    SELECT DISTINCT f.path, f.name 
                    FROM files f
                    WHERE (f.path LIKE ? OR f.name LIKE ?)
                    AND f.path NOT IN ({placeholders})
                    LIMIT ?;
                    """,
                    [word_like, word_like] + list(seen_paths)[:100] + [limit - len(all_results)]
                )
            else:
                cur = conn.execute(
                    """
                    SELECT DISTINCT f.path, f.name 
                    FROM files f
                    WHERE (f.path LIKE ? OR f.name LIKE ?)
                    LIMIT ?;
                    """,
                    (word_like, word_like, limit - len(all_results))
                )
            word_results = cur.fetchall()
            for r in word_results:
                if r[0] not in seen_paths:
                    all_results.append(r)
                    seen_paths.add(r[0])
                    if len(all_results) >= limit:
                        break
            if len(all_results) >= limit:
                break
    
    rows = [{"path": r[0], "name": r[1]} for r in all_results[:limit]]
    conn.close()
    return rows

def search_chunks(query: str, limit: int = 8) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    
    all_results = []
    seen_chunk_ids = set()
    
    # 1. LIKE 검색을 우선 사용 (한국어 검색에 더 효과적)
    like_term = f"%{q}%"
    cur = conn.execute(
        """
        SELECT DISTINCT c.text, f.path, c.id
        FROM chunks c
        JOIN files f ON f.id = c.file_id
        WHERE c.text LIKE ?
        LIMIT ?;
        """,
        (like_term, limit * 2)  # 더 많이 가져와서 중복 제거
    )
    like_results = cur.fetchall()
    for r in like_results:
        if r[2] not in seen_chunk_ids:
            all_results.append(r)
            seen_chunk_ids.add(r[2])
            if len(all_results) >= limit:
                break
    
    # 2. FTS5 검색 시도 (추가 결과)
    if len(all_results) < limit:
        try:
            search_term = q.replace('"','').replace("'", "")
            cur = conn.execute(
                """
                SELECT c.text, f.path, c.id
                FROM chunks_fts t
                JOIN chunks c ON c.id = t.rowid
                JOIN files f ON f.id = c.file_id
                WHERE chunks_fts MATCH ?
                LIMIT ?;
                """,
                (search_term, limit)
            )
            fts_results = cur.fetchall()
            for r in fts_results:
                if r[2] not in seen_chunk_ids:
                    all_results.append(r)
                    seen_chunk_ids.add(r[2])
                    if len(all_results) >= limit:
                        break
        except Exception:
            # FTS5 실패 시 무시
            pass
    
    # 3. 단어별 검색 (한국어 검색 개선)
    if len(all_results) < limit:
        words = q.split()
        for word in words:
            if len(word) < 2:  # 너무 짧은 단어는 스킵
                continue
            word_like = f"%{word}%"
            # 이미 본 청크 ID 제외
            if seen_chunk_ids:
                placeholders = ','.join(['?'] * min(len(seen_chunk_ids), 1000))
                cur = conn.execute(
                    f"""
                    SELECT DISTINCT c.text, f.path, c.id
                    FROM chunks c
                    JOIN files f ON f.id = c.file_id
                    WHERE c.text LIKE ?
                    AND c.id NOT IN ({placeholders})
                    LIMIT ?;
                    """,
                    [word_like] + list(seen_chunk_ids)[:1000] + [limit - len(all_results)]
                )
            else:
                cur = conn.execute(
                    """
                    SELECT DISTINCT c.text, f.path, c.id
                    FROM chunks c
                    JOIN files f ON f.id = c.file_id
                    WHERE c.text LIKE ?
                    LIMIT ?;
                    """,
                    (word_like, limit - len(all_results))
                )
            word_results = cur.fetchall()
            for r in word_results:
                if r[2] not in seen_chunk_ids:
                    all_results.append(r)
                    seen_chunk_ids.add(r[2])
                    if len(all_results) >= limit:
                        break
            if len(all_results) >= limit:
                break
    
    rows = [{"text": r[0], "path": r[1], "chunk_id": r[2]} for r in all_results[:limit]]
    conn.close()
    return rows
