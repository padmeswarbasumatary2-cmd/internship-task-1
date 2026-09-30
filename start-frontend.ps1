$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Installing frontend dependencies..."
& "C:\Program Files\nodejs\npm.cmd" --prefix frontend install

Write-Host "Starting frontend dev server..."
& "C:\Program Files\nodejs\npm.cmd" --prefix frontend run dev
