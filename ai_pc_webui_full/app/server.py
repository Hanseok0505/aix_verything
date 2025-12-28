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

app = FastAPI(title="AI PC", version="0.1.0")

class ChatReq(BaseModel):
    message: str

class IndexReq(BaseModel):
    root: str

class OpenReq(BaseModel):
    path: str

def get_provider():
    if settings.mode == "internal":
        return OpenAICompatibleProvider()
    return LocalStubProvider()

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "mode": settings.mode}

@app.post("/index")
def api_index(req: IndexReq):
    return index_folder(req.root)

@app.post("/search")
def api_search(req: ChatReq):
    return {"results": search_files(req.message, limit=20)}

@app.post("/open")
def api_open(req: OpenReq):
    return {"ok": open_in_explorer(req.path)}

@app.post("/chat")
def api_chat(req: ChatReq):
    q = req.message
    provider = get_provider()

    file_hits = search_files(q, limit=10)
    chunk_hits = search_chunks(q, limit=6)

    context_lines = []
    if file_hits:
        context_lines.append("## File matches")
        context_lines += [f"- {h['path']}" for h in file_hits]
    if chunk_hits:
        context_lines.append("\n## Content snippets")
        for h in chunk_hits:
            snippet = (h['text'] or "").strip().replace("\n"," ")
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            context_lines.append(f"- ({h['path']}) {snippet}")

    system = (
        "You are an assistant for finding and opening files on this PC. "
        "When user intent is to open, respond with a single line JSON like "
        "{"action":"open","path":"..."}. "
        "Otherwise, answer briefly and include the best matching paths."
    )
    messages = [
        {"role":"system","content":system},
        {"role":"user","content": f"User query: {q}\n\nContext:\n" + "\n".join(context_lines)}
    ]
    answer = provider.chat(messages)

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

    return {"answer": answer, "results": file_hits, "snippets": chunk_hits, "action": action}

# Serve UI
UI_DIR = __import__("os").path.join(__import__("os").path.dirname(__file__), "ui")
app.mount("/ui-static", StaticFiles(directory=UI_DIR), name="ui-static")

@app.get("/ui", response_class=HTMLResponse)
def ui():
    with open(__import__("os").path.join(UI_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()
