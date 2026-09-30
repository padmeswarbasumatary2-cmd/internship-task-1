$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Starting backend API..."
& py -m pip install -r backend/requirements.txt
Set-Location "$root\backend"
& py -m uvicorn app.main:app --host 0.0.0.0 --port 8000
