# EventEase Automated Environment Setup

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   EventEase -- Environment Setup & Database Initialization" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/4] Checking Python runtime..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "      Detected: $pyVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not found in PATH. Please install Python 3.10+ and re-run."
    exit 1
}

# 2. Virtual Environment Setup
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[2/4] Creating virtual environment at .venv..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "      Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[2/4] Existing virtual environment found at .venv." -ForegroundColor Green
}

# 3. Install Dependencies
Write-Host "[3/4] Installing / updating Python dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
$reqPath = Join-Path $projectRoot "requirements.txt"
& $venvPython -m pip install -r $reqPath --quiet
Write-Host "      Dependencies installed successfully." -ForegroundColor Green

# 4. Initialize Database
Write-Host "[4/4] Initializing SQLite database and seed data..." -ForegroundColor Yellow
$initScript = Join-Path $projectRoot "database\init_db.py"
& $venvPython $initScript

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "   EventEase Setup Completed Successfully!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  To run the web app:     .\scripts\run.ps1" -ForegroundColor White
Write-Host "  To run automated tests:  .\scripts\test.ps1" -ForegroundColor White
Write-Host "  To probe health:         .\scripts\health_check.ps1" -ForegroundColor White
Write-Host ""
