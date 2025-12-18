# ============================================================
# Terminal Recorder — Full Screen Buffer + Live Transcript
# ============================================================

# 1. Ensure logs folder exists
$logRoot = Join-Path $PSScriptRoot "logs"
if (!(Test-Path $logRoot)) {
    New-Item -ItemType Directory -Path $logRoot | Out-Null
}

# 2. Create timestamped output file
$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$logFile = Join-Path $logRoot "Terminal_$timestamp.txt"

Write-Host "`n[LOGGER] Terminal recorder started." -ForegroundColor Green
Write-Host "[LOGGER] Output will be saved to: $logFile`n" -ForegroundColor Green

# ============================================================
# PART 1 — Capture EVERYTHING already on screen
# ============================================================
$buffer = (Get-Host).UI.RawUI.GetBufferContents(
    (New-Object System.Management.Automation.Host.Coordinates 0,0),
    (New-Object System.Management.Automation.Host.Coordinates `
        ((Get-Host).UI.RawUI.BufferSize.Width - 1),
        ((Get-Host).UI.RawUI.CursorPosition.Y)
    )
)

$lines = @()
foreach ($row in $buffer) {
    $text = ""
    foreach ($cell in $row) { $text += $cell.Character }
    $lines += $text.TrimEnd()
}

$lines | Out-File -FilePath $logFile -Encoding UTF8

# ============================================================
# PART 2 — Begin live recording (everything after this point)
# ============================================================
Start-Transcript -Path $logFile -Append | Out-Null

Write-Host "[LOGGER] Live capture started..." -ForegroundColor Cyan
Write-Host "----------------------------------------"
Write-Host "Recording everything. Use:"
Write-Host "    Stop-Transcript"
Write-Host "to finish recording."
Write-Host "----------------------------------------"
