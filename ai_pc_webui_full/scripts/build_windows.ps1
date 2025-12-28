# Build Windows executables (run on Windows)
$ErrorActionPreference = "Stop"
if (!(Test-Path .venv)) {
  python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --clean --onefile run_web.py --name ai-pc-web
pyinstaller --noconfirm --clean --onefile run_desktop.py --name ai-pc-desktop

Write-Host "Built executables are in .\dist\"
