param(
    [string]$Phase = ""
)

Write-Host "=== OMNI Controller ===" -ForegroundColor Cyan

# Root path
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Correct GitGuardian path
$GitGuardianPath = Join-Path $Root "v2_core\system\git_tools\InteliGitGuardian.ps1"

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
