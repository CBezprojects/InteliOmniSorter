# ================================================================
# OMNI Post-Phase Hook System
# Called after any OMNI phase completes
# Responsibilities:
#   - Log completion
#   - Trigger Git Guardian
#   - (Future) Cleanup, backups, metrics, changelog updates
# ================================================================

param (
    [string]$PhaseName = "Unknown Phase"
)

Write-Host "=== OMNI Post-Phase Hook ==="
Write-Host "Phase completed: $PhaseName"
Write-Host "Running Git Guardian..."

# Detect repo root automatically (two levels up)
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$GitGuardianPath = Join-Path $RepoRoot "InteliGitGuardian.ps1"

if (Test-Path $GitGuardianPath) {
    powershell -ExecutionPolicy Bypass -File $GitGuardianPath
}
else {
    Write-Host "Git Guardian not found: $GitGuardianPath"
}
