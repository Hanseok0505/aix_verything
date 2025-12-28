import os, sqlite3
from app.config import settings

def get_conn():
    os.makedirs(os.path.dirname(settings.sqlite_path), exist_ok=True)
    conn = sqlite3.connect(settings.sqlite_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
      CREATE TABLE IF NOT EXISTS indexed_roots(
        id INTEGER PRIMARY KEY,
        root_path TEXT UNIQUE,
        indexed_at INTEGER,
        file_count INTEGER DEFAULT 0,
        chunk_count INTEGER DEFAULT 0
      );
    """)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE,
        name TEXT,
        ext TEXT,
        size INTEGER,
        mtime INTEGER,
        root_path TEXT
      );
    """)
    
    # 기존 DB 마이그레이션: root_path 컬럼 추가
    try:
        cur = conn.execute("PRAGMA table_info(files)")
        columns = [row[1] for row in cur.fetchall()]
        if 'root_path' not in columns:
            print("[DB Migration] Adding root_path column to files table...")
            conn.execute("ALTER TABLE files ADD COLUMN root_path TEXT")
            conn.commit()
            print("[DB Migration] root_path column added successfully")
    except Exception as e:
        print(f"[DB Migration] Error: {e}")
    conn.execute("""
      CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY,
        file_id INTEGER,
        chunk_index INTEGER,
        text TEXT,
        FOREIGN KEY(file_id) REFERENCES files(id)
      );
    """)
    conn.execute("""
      CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
      USING fts5(path, name, content='files', content_rowid='id');
    """)
    conn.execute("""
      CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
      USING fts5(text, content='chunks', content_rowid='id');
    """)
    conn.execute("""
      CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
        INSERT INTO files_fts(rowid, path, name) VALUES (new.id, new.path, new.name);
      END;
    """)
    conn.execute("""
      CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
        INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
      END;
    """)
    conn.commit()
    conn.close()
