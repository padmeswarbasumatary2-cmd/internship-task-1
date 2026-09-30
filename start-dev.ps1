$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting backend and frontend..."
$backend = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","$root\start-backend.ps1" -WorkingDirectory $root -PassThru
$frontend = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","$root\start-frontend.ps1" -WorkingDirectory $root -PassThru

Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
Write-Host "API docs: http://localhost:8000/docs"
Write-Host "Process IDs: Backend=$($backend.Id), Frontend=$($frontend.Id)"
