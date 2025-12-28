from typing import List, Dict
from app.db import get_conn

def search_files(query: str, limit: int = 20) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    
    # FTS5 MATCH와 LIKE 검색을 결합하여 부분 문자열 매칭 지원
    # FTS5는 정확한 단어 매칭이므로, LIKE로 부분 문자열 검색도 추가
    search_term = q.replace('"','')
    
    # FTS5 검색 시도
    cur = conn.execute(
        "SELECT path, name FROM files_fts WHERE files_fts MATCH ? LIMIT ?;",
        (search_term, limit)
    )
    fts_results = cur.fetchall()
    
    # 부분 문자열 매칭 (LIKE 검색) - FTS 결과가 적을 때 보완
    if len(fts_results) < limit:
        remaining = limit - len(fts_results)
        like_term = f"%{q}%"
        cur = conn.execute(
            """
            SELECT DISTINCT f.path, f.name 
            FROM files f
            WHERE (f.path LIKE ? OR f.name LIKE ?)
            AND f.path NOT IN (SELECT path FROM files_fts WHERE files_fts MATCH ?)
            LIMIT ?;
            """,
            (like_term, like_term, search_term, remaining)
        )
        like_results = cur.fetchall()
        fts_results.extend(like_results)
    
    rows = [{"path": r[0], "name": r[1]} for r in fts_results[:limit]]
    conn.close()
    return rows

def search_chunks(query: str, limit: int = 8) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    
    # FTS5 검색
    search_term = q.replace('"','')
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
    
    # 부분 문자열 매칭 (LIKE 검색) - FTS 결과가 적을 때 보완
    if len(fts_results) < limit:
        remaining = limit - len(fts_results)
        like_term = f"%{q}%"
        cur = conn.execute(
            """
            SELECT DISTINCT c.text, f.path, c.id
            FROM chunks c
            JOIN files f ON f.id = c.file_id
            WHERE c.text LIKE ?
            AND c.id NOT IN (
                SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ?
            )
            LIMIT ?;
            """,
            (like_term, search_term, remaining)
        )
        like_results = cur.fetchall()
        fts_results.extend(like_results)
    
    rows = [{"text": r[0], "path": r[1], "chunk_id": r[2]} for r in fts_results[:limit]]
    conn.close()
    return rows
