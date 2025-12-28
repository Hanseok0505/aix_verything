import os, time
from typing import Iterable, Dict, Any, List
from app.config import settings
from app.db import get_conn
from app.extractors import extract_text
from app.chunker import chunk_text

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
    exts = [e.strip().lower() for e in settings.index_exts.split(",") if e.strip()]
    conn = get_conn()
    indexed_files=0
    indexed_chunks=0
    skipped=0
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
                conn.execute("INSERT OR IGNORE INTO files(path,name,ext,size,mtime) VALUES (?,?,?,?,?);",
                             (path,name,ext,size,mtime))
                file_id = conn.execute("SELECT id FROM files WHERE path=?;", (path,)).fetchone()[0]

            indexed_files += 1

            text = extract_text(path)
            if not text:
                continue
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
            for idx, ch in enumerate(chunks):
                conn.execute("INSERT INTO chunks(file_id, chunk_index, text) VALUES (?,?,?);",
                             (file_id, idx, ch))
            indexed_chunks += len(chunks)

            if indexed_files % 25 == 0:
                conn.commit()
        except Exception:
            continue

    conn.commit()
    conn.close()
    return {"indexed_files": indexed_files, "indexed_chunks": indexed_chunks, "skipped": skipped}
