Write-Host "=== OMNI AUTO-PATCH START ===" -ForegroundColor Cyan

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$ControllerPath = Join-Path $Root "OMNI_Controller.ps1"
$ScaffolderPath = Join-Path $Root "OMNI_Phase3_Scaffolding.ps1"

# -------------------------------
# PATCH 1 – FIX OMNI_Controller.ps1
# -------------------------------

$ControllerContent = @'
param(
    [string]$Phase = ""
)

Write-Host "=== OMNI Controller ===" -ForegroundColor Cyan

# Root path
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Correct GitGuardian path
$GitGuardianPath = Join-Path $Root "InteliGitGuardian.ps1"

Write-Host "Executing Phase: $Phase" -ForegroundColor Yellow

switch ($Phase) {
    "V2 Scaffolding" {
        Write-Host "Phase action: V2 scaffolding already created by OMNI_Phase3_Scaffolding.ps1" -ForegroundColor Green
    }
    default {
        Write-Host "Unknown or empty phase: $Phase" -ForegroundColor Red
    }
}

Write-Host "=== OMNI Post-Phase Hook ===" -ForegroundColor Cyan
Write-Host "Phase completed: $Phase"

Write-Host "Running Git Guardian..." -ForegroundColor Cyan

if (Test-Path $GitGuardianPath) {
    powershell -ExecutionPolicy Bypass -File $GitGuardianPath
}
else {
    Write-Host "Git Guardian not found at: $GitGuardianPath" -ForegroundColor Red
}

Write-Host "=== Controller Complete ===" -ForegroundColor Cyan
'@

Set-Content -Path $ControllerPath -Value $ControllerContent -Encoding UTF8
Write-Host "[PATCHED] OMNI_Controller.ps1" -ForegroundColor Green

# -------------------------------
# PATCH 2 – FIX OMNI_Phase3_Scaffolding.ps1
# -------------------------------

$ScaffolderOriginal = Get-Content $ScaffolderPath -Raw

# Replace directory creation loop
$FixedLoop = @'
foreach ($dir in $dirs) {
    if (![string]::IsNullOrWhiteSpace($dir)) {
        if (!(Test-Path $dir)) {
            Write-Host "[CREATE] $dir"
            New-Item -ItemType Directory -Path $dir | Out-Null
        }
        else {
            Write-Host "[EXISTS] $dir"
        }
    }
}
'@

# Pattern to replace
$ScaffolderFixed = $ScaffolderOriginal -replace 'foreach\s*\(\$dir.*?\}\s*\}', $FixedLoop

Set-Content -Path $ScaffolderPath -Value $ScaffolderFixed -Encoding UTF8
Write-Host "[PATCHED] OMNI_Phase3_Scaffolding.ps1" -ForegroundColor Green

Write-Host "=== OMNI AUTO-PATCH COMPLETE ===" -ForegroundColor Cyan
Write-Host "You may now run:" -ForegroundColor Yellow
Write-Host 'powershell -ExecutionPolicy Bypass -File .\OMNI_Controller.ps1 -Phase "V2 Scaffolding"' -ForegroundColor White
