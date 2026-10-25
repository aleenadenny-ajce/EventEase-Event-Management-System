# EventEase Local Server Launcher

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Warning "Virtual environment not found. Running setup first..."
    & (Join-Path $PSScriptRoot "setup.ps1")
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   EventEase -- Starting Local Web Server" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Access URL:      http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Health Probe:    http://127.0.0.1:5000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Evaluation Demo Credentials:" -ForegroundColor Yellow
Write-Host "  Admin:        admin@eventease.local       / Admin@Password123" -ForegroundColor White
Write-Host "  Organizer:    organizer@eventease.local   / Organizer@Password123" -ForegroundColor White
Write-Host "  Participant:  participant@eventease.local / User@Password123" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $projectRoot
& $venvPython app.py
