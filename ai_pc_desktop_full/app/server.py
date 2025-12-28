import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.config import settings
from app.db import init_db
from app.indexer import index_folder
from app.search import search_files, search_chunks
from app.tools.file_ops import open_in_explorer

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.local_stub import LocalStubProvider
from app.providers.local_llamacpp import LocalLlamaCppProvider
from app.rag import search_rag
from app.delete_path import delete_indexed_path
from app.db import get_conn
import subprocess
import platform
import os
import sys

app = FastAPI(title="AI PC", version="0.1.0")

class ChatReq(BaseModel):
    message: str

class IndexReq(BaseModel):
    root: str  # 단일 경로 또는 세미콜론(;)으로 구분된 여러 경로

class OpenReq(BaseModel):
    path: str

class DeletePathReq(BaseModel):
    root_path: str

def get_provider():
    if settings.mode == "internal":
        return OpenAICompatibleProvider()
    elif settings.mode == "local":
        try:
            return LocalLlamaCppProvider()
        except Exception as e:
            # 로컬 모델이 없으면 stub 반환
            return LocalStubProvider()
    return LocalStubProvider()

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "mode": settings.mode}

@app.post("/index")
def api_index(req: IndexReq):
    # 여러 경로 지원 (세미콜론 또는 줄바꿈으로 구분)
    roots = [r.strip() for r in req.root.replace('\n', ';').split(';') if r.strip()]
    if not roots:
        return {"error": "경로가 없습니다"}
    
    results = []
    for root in roots:
        try:
            result = index_folder(root)
            result["root"] = root
            results.append(result)
        except Exception as e:
            results.append({"root": root, "error": str(e)})
    
    # 전체 요약
    total_files = sum(r.get("indexed_files", 0) for r in results)
    total_chunks = sum(r.get("indexed_chunks", 0) for r in results)
    total_vectors = sum(r.get("indexed_vectors", 0) for r in results)
    
    return {
        "results": results,
        "summary": {
            "total_roots": len(roots),
            "total_files": total_files,
            "total_chunks": total_chunks,
            "total_vectors": total_vectors
        }
    }

@app.post("/search")
def api_search(req: ChatReq):
    return {"results": search_files(req.message, limit=20)}

@app.post("/open")
def api_open(req: OpenReq):
    return {"ok": open_in_explorer(req.path)}

@app.get("/indexed-roots")
def get_indexed_roots():
    """인덱싱된 루트 경로 목록 가져오기"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT root_path, indexed_at, file_count, chunk_count
        FROM indexed_roots
        ORDER BY indexed_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return {
        "roots": [
            {
                "root_path": r[0],
                "indexed_at": r[1],
                "file_count": r[2],
                "chunk_count": r[3]
            }
            for r in rows
        ]
    }

@app.post("/delete-path")
def api_delete_path(req: DeletePathReq):
    """인덱싱된 경로 삭제 (DB + FAISS)"""
    try:
        result = delete_indexed_path(req.root_path)
        return result
    except Exception as e:
        return {"deleted": False, "error": str(e)}

@app.get("/select-folder")
def select_folder():
    """Windows 폴더 선택 대화상자 열기 (서버 측)"""
    if platform.system() != "Windows":
        return {"error": "Windows에서만 사용 가능합니다"}
    
    try:
        # 별도 Python 스크립트로 실행 (GUI가 제대로 나타나도록)
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "select_folder.py")
        script_path = os.path.abspath(script_path)
        
        python_exe = sys.executable
        
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=120,  # 2분 타임아웃
            creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output == "CANCELLED":
                return {"path": None, "cancelled": True}
            elif output.startswith("ERROR:"):
                error_msg = output.replace("ERROR: ", "")
                return {"error": error_msg}
            elif output:
                return {"path": output}
            else:
                return {"path": None, "cancelled": True}
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return {"error": f"폴더 선택 실패: {error_msg}"}
            
    except subprocess.TimeoutExpired:
        return {"error": "폴더 선택 대화상자가 시간 초과되었습니다. 경로를 직접 입력해주세요."}
    except FileNotFoundError:
        # 스크립트가 없으면 직접 tkinter 사용
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            folder_path = filedialog.askdirectory(
                title="인덱싱할 폴더를 선택하세요",
                mustexist=True
            )
            
            root.destroy()
            
            if folder_path:
                return {"path": folder_path}
            else:
                return {"path": None, "cancelled": True}
        except Exception as e:
            return {"error": f"폴더 선택 실패: {str(e)}. 경로를 직접 입력해주세요."}
    except Exception as e:
        return {"error": f"폴더 선택 실패: {str(e)}. 경로를 직접 입력해주세요."}

@app.post("/chat")
def api_chat(req: ChatReq):
    q = req.message
    try:
        provider = get_provider()
    except Exception as e:
        return {
            "error": f"LLM 프로바이더 초기화 실패: {str(e)}",
            "answer": f"오류: LLM을 사용할 수 없습니다. 설정을 확인하세요.\n\n오류 내용: {str(e)}",
            "results": [],
            "snippets": [],
            "rag_snippets": [],
            "action": None
        }

    # 파일명/경로 기반 검색
    file_hits = search_files(q, limit=10)
    
    # 텍스트 내용 기반 검색 (FTS)
    chunk_hits = search_chunks(q, limit=6)
    
    # RAG 기반 의미 검색 (임베딩 활성화 시)
    rag_hits = search_rag(q, limit=5) if settings.enable_embeddings else []

    context_lines = []
    if file_hits:
        context_lines.append("## File matches")
        context_lines += [f"- {h['path']}" for h in file_hits]
    if chunk_hits:
        context_lines.append("\n## Content snippets (keyword match)")
        for h in chunk_hits:
            snippet = (h['text'] or "").strip().replace("\n"," ")
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            context_lines.append(f"- ({h['path']}) {snippet}")
    if rag_hits:
        context_lines.append("\n## Content snippets (semantic match)")
        for h in rag_hits:
            snippet = (h['text'] or "").strip().replace("\n"," ")
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            context_lines.append(f"- ({h['path']}) {snippet}")

    system = (
        "You are an assistant for finding and opening files on this PC. "
        "When user intent is to open, respond with a single line JSON like "
        '{"action":"open","path":"..."}. '
        "Otherwise, answer briefly and include the best matching paths."
    )
    messages = [
        {"role":"system","content":system},
        {"role":"user","content": f"User query: {q}\n\nContext:\n" + "\n".join(context_lines)}
    ]
    
    try:
        answer = provider.chat(messages)
    except Exception as e:
        error_msg = f"LLM 호출 실패: {str(e)}"
        if settings.mode == "internal":
            error_msg += f"\n\n내부 API 서버가 실행 중인지 확인하세요:\n- URL: {settings.internal_base_url}\n- 모델: {settings.internal_model}"
        elif settings.mode == "local":
            error_msg += f"\n\n로컬 모델 파일을 확인하세요:\n- 경로: {settings.local_gguf_path}"
        
        return {
            "error": error_msg,
            "answer": error_msg,
            "results": file_hits,
            "snippets": chunk_hits,
            "rag_snippets": rag_hits,
            "action": None
        }

    # Try to parse tool-like JSON (optional)
    action = None
    try:
        m = answer.strip()
        if m.startswith("{") and m.endswith("}"):
            obj = json.loads(m)
            if obj.get("action") == "open" and obj.get("path"):
                action = obj
    except Exception:
        pass

    return {
        "answer": answer, 
        "results": file_hits, 
        "snippets": chunk_hits,  # chunk 내용 포함
        "rag_snippets": rag_hits,  # RAG chunk 내용 포함
        "action": action
    }

# Serve UI
UI_DIR = __import__("os").path.join(__import__("os").path.dirname(__file__), "ui")
app.mount("/ui-static", StaticFiles(directory=UI_DIR), name="ui-static")

@app.get("/ui", response_class=HTMLResponse)
def ui():
    with open(__import__("os").path.join(UI_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()
