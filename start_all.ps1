$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting AI-Powered Enterprise Data Analytics Platform (PowerShell)  " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Launching Backend API on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$BackendDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching Frontend UI on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$FrontendDir'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "`nOpening browser to http://localhost:3000 ..." -ForegroundColor Green
Start-Process "http://localhost:3000"
