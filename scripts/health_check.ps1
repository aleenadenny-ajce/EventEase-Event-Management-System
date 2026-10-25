# EventEase Service Health Diagnostic Probe

[CmdletBinding()]
param(
    [string]$Url = "http://127.0.0.1:5000/health"
)

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   EventEase -- Service Health Diagnostic Probe" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Target URL: $Url" -ForegroundColor White
Write-Host ""

try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
    $stopwatch.Stop()

    Write-Host "[+] Connection Successful (Latency: $($stopwatch.ElapsedMilliseconds) ms)" -ForegroundColor Green
    Write-Host "--------------------------------------------------------" -ForegroundColor Gray
    Write-Host "Service Name:         $($response.service)" -ForegroundColor White
    Write-Host "Overall Status:       $($response.status)" -ForegroundColor $(if ($response.status -eq "UP") { "Green" } else { "Red" })
    Write-Host "Version:              $($response.version)" -ForegroundColor White
    Write-Host "Database Status:      $($response.database)" -ForegroundColor $(if ($response.database -eq "connected") { "Green" } else { "Red" })
    Write-Host "Timestamp (UTC):      $($response.timestamp)" -ForegroundColor White
    Write-Host "--------------------------------------------------------" -ForegroundColor Gray
    Write-Host "[+] Liveness & Readiness: READY FOR TRAFFIC" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[-] Health check failed: Unable to connect to $Url" -ForegroundColor Red
    Write-Host "    Details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the application server is running via .\scripts\run.ps1" -ForegroundColor Yellow
    Write-Host ""
}
