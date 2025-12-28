# AI PC (Local File RAG) — Web UI / Desktop App

This repo contains two runnable variants:

- **Variant A (Web UI)**: FastAPI backend + single-page HTML UI served at `/ui`
- **Variant B (Desktop App)**: A lightweight desktop wrapper (pywebview) that starts the same backend and embeds it in a desktop window.

## What this does (MVP)
- Index a folder into **SQLite (metadata + FTS)** and **FAISS (optional embeddings)**.
- Search by filename/path/content keywords.
- Chat endpoint that:
  - runs a fast search first
  - optionally does RAG retrieval (if embeddings are enabled)
  - calls an LLM provider:
    - **Internal proxy (OpenAI-compatible)** (recommended)
    - **Local LLM** is optional and not bundled by default
- Open a file/folder in Explorer/Finder (or xdg-open on Linux).

## Important
- This project is designed to run fully locally.  
- If you enable **internal proxy**, the app sends only the **retrieved snippets + paths** to your internal LLM endpoint.

---

## Quick start (Dev)

### 1) Create venv and install deps
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure
Copy `.env.example` to `.env` and edit as needed.

### 3) Run
Variant A (Web UI):
```bash
python run_web.py
```
Then open:
- http://127.0.0.1:8000/ui

Variant B (Desktop):
```bash
python run_desktop.py
```

### 4) Index a folder
Use the UI "Index Folder" panel, or call:
```bash
python cli_index.py --root "C:\\your\\folder"
```

---

## Build executables (Windows)
We include a build script using PyInstaller. Run in PowerShell:
```powershell
./scripts/build_windows.ps1
```
Outputs go to `dist/`.

## Build executables (macOS/Linux)
```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile run_web.py --name ai-pc-web
pyinstaller --noconfirm --clean --onefile run_desktop.py --name ai-pc-desktop
```

> Note: the sandbox build attached here is **Linux**. For Windows EXE, run the build script on Windows.
