# ======================================================
# InteliOmniSorter — Terminal Session Recorder v1
# ======================================================

$ErrorActionPreference = "Stop"

$RepoRoot = Get-Location
$LogRoot  = Join-Path $RepoRoot "logs\terminal"

if (!(Test-Path $LogRoot)) {
    New-Item -ItemType Directory -Path $LogRoot | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile   = Join-Path $LogRoot "terminal_session_$Timestamp.txt"

Write-Host ""
Write-Host "[Terminal Recorder] STARTING SESSION" -ForegroundColor Green
Write-Host "[Terminal Recorder] Log file:" -ForegroundColor Cyan
Write-Host $LogFile
Write-Host ""

Start-Transcript -Path $LogFile -Append -NoClobber

Write-Host "[Terminal Recorder] Recording active."
Write-Host "[Terminal Recorder] Use Stop-TerminalSession.ps1 to end."
Write-Host ""
