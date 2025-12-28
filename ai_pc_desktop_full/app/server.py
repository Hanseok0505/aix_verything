import json
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.config import settings
from app.db import init_db
from app.indexer import index_folder
from app.search import search_files, search_chunks
from app.tools.file_ops import open_in_explorer, open_file

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
    force: bool = False  # 강제 삭제 모드

class SettingsReq(BaseModel):
    mode: str = None  # "internal" or "local"
    internal_base_url: str = None
    internal_api_key: str = None
    internal_model: str = None
    local_gguf_path: str = None
    use_proxy: bool = None
    proxy_url: str = None
    proxy_api_key: str = None

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

@app.get("/settings")
def get_settings():
    """현재 설정 가져오기"""
    return {
        "mode": settings.mode,
        "internal_base_url": settings.internal_base_url,
        "internal_api_key": settings.internal_api_key,
        "internal_model": settings.internal_model,
        "local_gguf_path": settings.local_gguf_path,
        "enable_embeddings": settings.enable_embeddings,
        "use_proxy": settings.use_proxy,
        "proxy_url": settings.proxy_url,
        "proxy_api_key": settings.proxy_api_key
    }

@app.post("/settings")
def update_settings(req: SettingsReq):
    """설정 업데이트"""
    import os
    from pathlib import Path
    
    env_path = Path(".env")
    env_content = ""
    
    # 기존 .env 파일 읽기
    if env_path.exists():
        env_content = env_path.read_text(encoding='utf-8')
    else:
        # env_example.txt에서 기본값 가져오기
        example_path = Path("env_example.txt")
        if example_path.exists():
            env_content = example_path.read_text(encoding='utf-8')
    
    # 설정 업데이트
    updates = {}
    if req.mode is not None:
        updates["AI_PC_MODE"] = req.mode
    if req.internal_base_url is not None:
        updates["INTERNAL_BASE_URL"] = req.internal_base_url
    if req.internal_api_key is not None:
        updates["INTERNAL_API_KEY"] = req.internal_api_key
    if req.internal_model is not None:
        updates["INTERNAL_MODEL"] = req.internal_model
    if req.local_gguf_path is not None:
        updates["LOCAL_GGUF_PATH"] = req.local_gguf_path
    if req.use_proxy is not None:
        updates["USE_PROXY"] = "true" if req.use_proxy else "false"
    if req.proxy_url is not None:
        updates["PROXY_URL"] = req.proxy_url
    if req.proxy_api_key is not None:
        updates["PROXY_API_KEY"] = req.proxy_api_key
    
    # .env 파일 업데이트
    import re
    for key, value in updates.items():
        pattern = rf"^{key}=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, env_content, re.MULTILINE):
            env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
        else:
            # 키가 없으면 추가
            env_content += f"\n{key}={value}\n"
    
    env_path.write_text(env_content, encoding='utf-8')
    
    # 설정 리로드 (다음 요청부터 적용)
    # 현재 세션에서는 변경사항이 반영되지 않으므로 서버 재시작 필요 안내
    return {
        "success": True,
        "message": "설정이 저장되었습니다. 변경사항을 적용하려면 서버를 재시작하세요.",
        "settings": {**updates}
    }

@app.get("/ollama-models")
def get_ollama_models():
    """Ollama에서 사용 가능한 모델 목록 가져오기"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {"models": models, "available": True}
        else:
            return {"models": [], "available": False, "error": "Ollama 서버 응답 오류"}
    except Exception as e:
        return {"models": [], "available": False, "error": str(e)}

@app.post("/index")
def api_index(req: IndexReq):
    # 여러 경로 지원 (세미콜론 또는 줄바꿈으로 구분)
    roots = [r.strip() for r in req.root.replace('\n', ';').split(';') if r.strip()]
    if not roots:
        return {"error": "경로가 없습니다"}
    
    results = []
    for root in roots:
        try:
            # 경로 정규화 및 검증
            import os
            # 빈 경로나 잘못된 형식 처리
            root = root.strip()
            if not root:
                continue
            
            # "D:W" 같은 잘못된 형식 처리
            if len(root) == 3 and root[1] == ':' and root[2].isalpha():
                # "D:W" -> "D:\" 또는 "D:/"로 변환
                root = root[:2] + os.sep
            
            # 경로 정규화
            try:
                normalized_root = os.path.normpath(os.path.abspath(root))
            except Exception as e:
                results.append({"root": root, "error": f"경로 정규화 실패: {str(e)}"})
                continue
            
            # 잘못된 경로 형식 검증 (예: "D:W" 같은 경우)
            if len(normalized_root) == 2 and normalized_root[1] == ':':
                # 드라이브 루트만 있는 경우 백슬래시 추가
                normalized_root = normalized_root + os.sep
            
            # 경로 존재 확인
            if not os.path.exists(normalized_root):
                results.append({"root": root, "error": f"경로가 존재하지 않습니다: {normalized_root}"})
                continue
            
            # 기존 인덱싱된 경로가 있으면 삭제 후 재인덱싱 (강제 재인덱싱)
            from app.delete_path import delete_indexed_path
            try:
                # 정규화된 경로와 원본 경로 모두로 삭제 시도
                delete_result = delete_indexed_path(normalized_root)
                if not delete_result.get("deleted") and root != normalized_root:
                    # 원본 경로로도 삭제 시도
                    delete_result = delete_indexed_path(root)
                
                if delete_result.get("deleted"):
                    print(f"[Index] 기존 인덱싱 데이터 삭제: {normalized_root} ({delete_result.get('deleted_files', 0)}개 파일)")
            except Exception as e:
                # 삭제 실패해도 계속 진행
                print(f"[Index] 기존 데이터 삭제 실패 (무시): {e}")
            
            result = index_folder(normalized_root)
            result["root"] = normalized_root  # 정규화된 경로 사용
            results.append(result)
        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            print(f"[Index API] Error indexing {root}: {error_detail}")
            results.append({"root": root, "error": str(e)})
            print(f"[Index] 오류: {e}")
            traceback.print_exc()
    
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
    """파일이 있는 폴더를 열고 파일을 선택합니다."""
    return {"ok": open_in_explorer(req.path)}

@app.post("/open-file")
def api_open_file(req: OpenReq):
    """파일을 기본 애플리케이션으로 직접 엽니다."""
    return {"ok": open_file(req.path)}

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
        import os
        # 경로 정규화
        root_path = req.root_path.strip()
        
        # "D:W" 같은 잘못된 형식 처리
        if len(root_path) == 3 and root_path[1] == ':' and root_path[2].isalpha():
            root_path = root_path[:2] + os.sep
        
        # 정규화된 경로로 삭제 시도
        result = delete_indexed_path(root_path)
        
        # 삭제 실패 시 원본 경로로도 시도
        if not result.get("deleted"):
            try:
                normalized = os.path.normpath(os.path.abspath(root_path))
                if normalized != root_path:
                    result = delete_indexed_path(normalized)
            except Exception:
                pass
        
        # 여전히 실패하면 강제 삭제 (indexed_roots에서만)
        if not result.get("deleted"):
            conn = get_conn()
            cur = conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (req.root_path,))
            deleted_count = cur.rowcount
            if deleted_count == 0:
                # 정규화된 경로로도 시도
                try:
                    normalized = os.path.normpath(os.path.abspath(req.root_path))
                    cur = conn.execute("DELETE FROM indexed_roots WHERE root_path = ?", (normalized,))
                    deleted_count = cur.rowcount
                except Exception:
                    pass
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                return {"deleted": True, "root_path": req.root_path, "deleted_files": 0, "deleted_chunks": 0, "deleted_vectors": 0, "message": "인덱싱된 경로만 삭제되었습니다 (파일 없음)"}
        
        return result
    except Exception as e:
        import traceback
        print(f"[Delete Path API] Error: {traceback.format_exc()}")
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
            "action": None,
            "model_info": {
                "mode": settings.mode,
                "model": "unknown",
                "using_llm": False
            }
        }

    # 파일명/경로 기반 검색
    file_hits = search_files(q, limit=10)
    
    # 텍스트 내용 기반 검색 (FTS)
    chunk_hits = search_chunks(q, limit=6)
    
    # RAG 기반 의미 검색 (임베딩 활성화 시)
    rag_hits = search_rag(q, limit=5) if settings.enable_embeddings else []

    # 디버깅: 검색 결과 로깅
    print(f"[Chat] Query: {q}")
    print(f"[Chat] File hits: {len(file_hits)}, Chunk hits: {len(chunk_hits)}, RAG hits: {len(rag_hits)}")
    
    # 검색 결과 상세 로깅
    if file_hits:
        print(f"[Chat] File hits sample: {file_hits[0]['path'] if file_hits else 'None'}")
    if chunk_hits:
        print(f"[Chat] Chunk hits sample: {chunk_hits[0]['path'] if chunk_hits else 'None'}")

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

    # 검색 결과가 없을 때 명확한 안내
    has_results = len(file_hits) > 0 or len(chunk_hits) > 0 or len(rag_hits) > 0
    if not has_results:
        context_lines.append("## No matching files found")
        context_lines.append("No files or content matched the search query in the indexed database.")
        context_lines.append("DO NOT list any example paths or make up file paths.")
        print(f"[Chat] WARNING: No search results found for query: {q}")

    system = (
        "You are an assistant for finding and opening files on this PC. "
        "CRITICAL RULES:\n"
        "1. ALWAYS check the Context section below FIRST before responding.\n"
        "2. If the Context section contains '## File matches' or '## Content snippets', you MUST use those results.\n"
        "3. ONLY use file paths that are EXACTLY listed in the Context section below.\n"
        "4. NEVER invent, make up, or create example file paths.\n"
        "5. NEVER use placeholder paths like 'C:\\Users\\username\\...' or any paths with 'username'.\n"
        "6. If the Context section shows 'No matching files found', you MUST respond with ONLY: 'No matching files found in the indexed database.'\n"
        "7. Do NOT list any 'Best matching paths' or example paths if no files were found.\n"
        "8. When files ARE found in Context, you MUST reference them in your answer. List the exact paths from the Context section.\n"
        "9. When user asks a question, answer based on the content snippets provided in the Context section.\n"
        "10. When user intent is to open a file, respond with a single line JSON like "
        '{"action":"open","path":"..."} using ONLY paths from the Context section.\n'
        "11. If Context shows 'No matching files found', your response must be brief and state only that no files matched.\n"
        "12. IMPORTANT: If Context contains file matches or content snippets, you MUST acknowledge them and use them in your response."
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
            "action": None,
            "model_info": {
                "mode": settings.mode,
                "model": settings.internal_model if settings.mode == "internal" else "local",
                "using_llm": False
            }
        }

    # 검색 결과가 없을 때 가짜 경로 필터링
    if not has_results:
        # 가짜 경로 패턴 감지 및 제거
        # username, example, sample 등의 가짜 경로 패턴 제거
        fake_patterns = [
            r'C:\\Users\\username\\[^\n]*',
            r'C:\\Users\\[^\\]+\\Desktop\\[^\n]*',
            r'C:\\Users\\[^\\]+\\Downloads\\[^\n]*',
            r'Best matching paths?:?\s*\n',
            r'-\s*C:\\Users\\[^\\]+\\[^\n]*',
        ]
        
        # 실제 검색된 경로 목록 생성
        valid_paths = set()
        for hit in file_hits + chunk_hits + rag_hits:
            if 'path' in hit:
                valid_paths.add(hit['path'])
        
        # 가짜 경로가 포함되어 있고 실제 경로가 없으면 응답 수정
        has_fake_path = any(re.search(pattern, answer, re.IGNORECASE) for pattern in fake_patterns)
        if has_fake_path and not valid_paths:
            # 가짜 경로 제거하고 간단한 메시지로 대체
            answer = "No matching files found in the indexed database."
        elif has_fake_path:
            # 가짜 경로만 제거하고 실제 경로는 유지
            for pattern in fake_patterns:
                answer = re.sub(pattern, '', answer, flags=re.IGNORECASE | re.MULTILINE)
            answer = answer.strip()

    # Try to parse tool-like JSON (optional)
    action = None
    try:
        m = answer.strip()
        if m.startswith("{") and m.endswith("}"):
            obj = json.loads(m)
            if obj.get("action") == "open" and obj.get("path"):
                # 실제 검색 결과에 있는 경로인지 확인
                valid_paths = {h.get('path') for h in file_hits + chunk_hits + rag_hits if h.get('path')}
                if obj.get("path") in valid_paths:
                    action = obj
                else:
                    # 가짜 경로이므로 action 제거
                    action = None
    except Exception:
        pass

    # 모델 정보 추가
    model_info = {
        "mode": settings.mode,
        "model": settings.internal_model if settings.mode == "internal" else "local",
        "using_llm": True
    }
    
    return {
        "answer": answer, 
        "results": file_hits, 
        "snippets": chunk_hits,  # chunk 내용 포함
        "rag_snippets": rag_hits,  # RAG chunk 내용 포함
        "action": action,
        "model_info": model_info
    }

# Serve UI
UI_DIR = __import__("os").path.join(__import__("os").path.dirname(__file__), "ui")
app.mount("/ui-static", StaticFiles(directory=UI_DIR), name="ui-static")

@app.get("/ui", response_class=HTMLResponse)
def ui():
    with open(__import__("os").path.join(UI_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()
