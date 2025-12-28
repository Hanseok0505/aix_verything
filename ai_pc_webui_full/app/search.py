from typing import List, Dict
from app.db import get_conn

def search_files(query: str, limit: int = 20) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    cur = conn.execute(
        "SELECT path, name FROM files_fts WHERE files_fts MATCH ? LIMIT ?;",
        (q.replace('"',''), limit)
    )
    rows = [{"path": r[0], "name": r[1]} for r in cur.fetchall()]
    conn.close()
    return rows

def search_chunks(query: str, limit: int = 8) -> List[Dict]:
    q = (query or "").strip()
    if not q:
        return []
    conn = get_conn()
    cur = conn.execute(
        """
        SELECT c.text, f.path
        FROM chunks_fts t
        JOIN chunks c ON c.id = t.rowid
        JOIN files f ON f.id = c.file_id
        WHERE chunks_fts MATCH ?
        LIMIT ?;
        """,
        (q.replace('"',''), limit)
    )
    rows = [{"text": r[0], "path": r[1]} for r in cur.fetchall()]
    conn.close()
    return rows
