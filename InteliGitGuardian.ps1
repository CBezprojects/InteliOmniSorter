# ============================================================
# InteliGitGuardian.ps1
# Automatic Commit + Push + Safety Checks for InteliOmniSorter
# Completely ASCII Safe Version
# ============================================================

Write-Host "=== InteliOmniSorter - Git Guardian ===" -ForegroundColor Cyan

# Detect repo root (script location)
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

Write-Host "[OK] Repo root set to: $RepoRoot" -ForegroundColor Green

# --------------------------------------------
# SETTINGS
# --------------------------------------------
$MaxFileSizeMB = 50
$ForbiddenExtensions = @(".zip", ".whl", ".7z", ".mp4", ".avi", ".mov", ".mkv")

# --------------------------------------------
# FUNCTION: Check for large files
# --------------------------------------------
function Test-LargeFiles {
    Write-Host "Checking for large files (greater than $MaxFileSizeMB MB)..." -ForegroundColor Yellow
    $LargeFiles = Get-ChildItem -Path $RepoRoot -Recurse -File | 
                  Where-Object { $_.Length -gt ($MaxFileSizeMB * 1MB) }

    if ($LargeFiles.Count -gt 0) {
        Write-Host "ERROR: Large files detected:" -ForegroundColor Red
        $LargeFiles | ForEach-Object { Write-Host (" - " + $_.FullName) -ForegroundColor Red }
        return $false
    }

    Write-Host "[OK] No large files detected." -ForegroundColor Green
    return $true
}

# --------------------------------------------
# FUNCTION: Check forbidden file types
# --------------------------------------------
function Test-Forbidden {
    Write-Host "Checking for forbidden file extensions..." -ForegroundColor Yellow

    $Detected = @()

    foreach ($ext in $ForbiddenExtensions) {
        $Detected += Get-ChildItem -Recurse -File | Where-Object { $_.Extension -eq $ext }
    }

    if ($Detected.Count -gt 0) {
        Write-Host "ERROR: Forbidden file types found:" -ForegroundColor Red
        $Detected | ForEach-Object { Write-Host (" - " + $_.FullName) -ForegroundColor Red }
        return $false
    }

    Write-Host "[OK] No forbidden file types found." -ForegroundColor Green
    return $true
}

# --------------------------------------------
# FUNCTION: Safe Commit
# --------------------------------------------
function Invoke-SafeCommit {
    Write-Host "Staging changes..." -ForegroundColor Yellow
    git add .

    $Status = git status --porcelain

    if (-not $Status) {
        Write-Host "[INFO] Nothing to commit. Working tree clean." -ForegroundColor DarkGray
        return $false
    }

    Write-Host "Committing changes..." -ForegroundColor Yellow
    git commit -m "Auto-commit: Git Guardian update"

    Write-Host "[OK] Commit complete." -ForegroundColor Green
    return $true
}

# --------------------------------------------
# FUNCTION: Repack Repo
# --------------------------------------------
function Invoke-Repack {
    Write-Host "Repacking repository to avoid large push bundles..." -ForegroundColor Yellow
    git gc --prune=now | Out-Null
    git repack -adf --depth=1 --window=1 | Out-Null
    Write-Host "[OK] Repack complete." -ForegroundColor Green
}

# --------------------------------------------
# FUNCTION: Safe Push
# --------------------------------------------
function Invoke-SafePush {

    Write-Host "Attempting safe thin push..." -ForegroundColor Yellow

    try {
        git push --thin origin main
        Write-Host "[OK] Push successful." -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[WARN] Thin push failed. Retrying with force-safe push..." -ForegroundColor Yellow

        try {
            git push origin main --force-with-lease
            Write-Host "[OK] Force-with-lease push successful." -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "ERROR: Push failed after retries." -ForegroundColor Red
            return $false
        }
    }
}

# --------------------------------------------
# RUN SAFETY CHECKS
# --------------------------------------------

if (-not (Test-LargeFiles)) { exit 1 }
if (-not (Test-Forbidden)) { exit 1 }

# --------------------------------------------
# REPACK REPO
# --------------------------------------------
Invoke-Repack

# --------------------------------------------
# COMMIT CHANGES
# --------------------------------------------
$Committed = Invoke-SafeCommit

if (-not $Committed) {
    Write-Host "[Git Guardian] No changes to push." -ForegroundColor Cyan
    exit 0
}

# --------------------------------------------
# PUSH CHANGES
# --------------------------------------------
Invoke-SafePush | Out-Null

Write-Host "=== Git Guardian Complete ===" -ForegroundColor Cyan
