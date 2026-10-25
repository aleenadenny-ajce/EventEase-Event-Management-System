# EventEase Automated Test Runner

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPytest = Join-Path $projectRoot ".venv\Scripts\pytest.exe"

if (-not (Test-Path $venvPytest)) {
    Write-Warning "Pytest not found in virtual environment. Running setup first..."
    & (Join-Path $PSScriptRoot "setup.ps1")
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   EventEase -- Running Automated Pytest Test Suite" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $projectRoot
& $venvPytest -v --tb=short

$testExitCode = $LASTEXITCODE

Write-Host ""
if ($testExitCode -eq 0) {
    Write-Host "[+] All EventEase test suites passed successfully!" -ForegroundColor Green
} else {
    Write-Host "[-] Test suite encountered failures. Exit code: $testExitCode" -ForegroundColor Red
}
Write-Host ""

exit $testExitCode
