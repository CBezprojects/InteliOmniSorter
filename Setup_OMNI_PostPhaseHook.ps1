# ================================================================
# Setup_OMNI_PostPhaseHook.ps1
# Creates OMNI Post-Phase Hook System + hook script
# ASCII-SAFE / Ready to Run
# ================================================================

Write-Host "=== Installing OMNI Post-Phase Hook System ==="

# Detect repo root (folder where script is run)
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

# ------------------------------------------------------------
# CREATE FOLDER STRUCTURE
# ------------------------------------------------------------
$HookFolder = Join-Path $RepoRoot "v2_core\system\hooks"

if (!(Test-Path $HookFolder)) {
    Write-Host "Creating folder: $HookFolder"
    New-Item -ItemType Directory -Force -Path $HookFolder | Out-Null
} else {
    Write-Host "Folder already exists: $HookFolder"
}

# ------------------------------------------------------------
# GENERATE post_phase.ps1
# ------------------------------------------------------------
$PostPhaseFile = Join-Path $HookFolder "post_phase.ps1"

$PostPhaseContent = @"
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
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$GuardianPath = Join-Path $RepoRoot "InteliGitGuardian.ps1"

if (Test-Path $GuardianPath) {
    powershell -ExecutionPolicy Bypass -File $GuardianPath
}
else {
    Write-Host "Git Guardian not found: $GuardianPath"
}
"@

Write-Host "Generating post_phase.ps1..."
$PostPhaseContent | Out-File -FilePath $PostPhaseFile -Encoding ASCII -Force

Write-Host "[OK] post_phase.ps1 created."

# ------------------------------------------------------------
# DISPLAY HOW TO CALL THE HOOK
# ------------------------------------------------------------

Write-Host ""
Write-Host "==============================================================="
Write-Host " HOW TO USE THE OMNI POST-PHASE HOOK"
Write-Host "==============================================================="
Write-Host ""
Write-Host "Add the following line at the END of any OMNI Phase Script:"
Write-Host ""
Write-Host "powershell -ExecutionPolicy Bypass -File `"v2_core/system/hooks/post_phase.ps1`" -PhaseName `"Phase 3 Scaffolding`""
Write-Host ""
Write-Host "Examples:"
Write-Host "Phase 3:"
Write-Host "  powershell -ExecutionPolicy Bypass -File `"v2_core/system/hooks/post_phase.ps1`" -PhaseName `"V2 Core Scaffolding`""
Write-Host ""
Write-Host "Phase 4:"
Write-Host "  powershell -ExecutionPolicy Bypass -File `"v2_core/system/hooks/post_phase.ps1`" -PhaseName `"Sort Engine Implementation`""
Write-Host ""
Write-Host "Phase 5:"
Write-Host "  powershell -ExecutionPolicy Bypass -File `"v2_core/system/hooks/post_phase.ps1`" -PhaseName `"Packaging`""
Write-Host ""
Write-Host "==============================================================="
Write-Host " OMNI Post-Phase Hook System Installation Complete"
Write-Host "==============================================================="
