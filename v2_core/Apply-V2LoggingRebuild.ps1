Write-Host "`n=== InteliOmniSorter V2 Logging Rebuild ===`n" -ForegroundColor Cyan

# -----------------------------------------------------
# 0) Helper function: Safe write with backup
# -----------------------------------------------------
function Write-WithBackup {
    param(
        [string]$Path,
        [string]$Content
    )

    $backup = "$Path.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $Path $backup -Force
    Set-Content -Path $Path -Value $Content -Encoding UTF8

    Write-Host "[OK] Updated: $Path (backup saved)" -ForegroundColor Green
}

# -----------------------------------------------------
# 1) Create Logger Module
# -----------------------------------------------------
Write-Host "`n[1] Creating V2 Logger Module..." -ForegroundColor Yellow

$loggerPath = "v2_core/system/logger"
if (!(Test-Path $loggerPath)) { New-Item -ItemType Directory -Path $loggerPath | Out-Null }

$loggerCode = @'
from pathlib import Path
from datetime import datetime

def get_log_path(engine_name):
    root = Path(__file__).resolve().parents[3] / "logs" / "engines"
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return root / f"{engine_name}_{timestamp}.log"

def write_log(path, message):
    with open(path, "a", encoding="utf8") as f:
        f.write(message + "\\n")
'@

Set-Content "$loggerPath\logger.py" -Value $loggerCode -Encoding UTF8
Write-Host "[OK] Logger created!" -ForegroundColor Green

# -----------------------------------------------------
# 2) Patch SortEngine to use file logs only
# -----------------------------------------------------
Write-Host "`n[2] Patching SortEngine..." -ForegroundColor Yellow

$sortPath = "v2_core/engines/sorter/sort_engine.py"
$sortCode = Get-Content $sortPath -Raw

# Remove print logging
$sortCode = $sortCode -replace "print\(entry\)", "write_log(self.log_file, entry)"

# Add logger imports + file log init
$inject = @'
from v2_core.system.logger.logger import get_log_path, write_log

def __post_init__(self):
    self.log_file = get_log_path("sort_engine")
'@

$sortCode = $sortCode -replace "class SortEngine:", "class SortEngine:`n    $inject"

Write-WithBackup -Path $sortPath -Content $sortCode

# -----------------------------------------------------
# 3) Patch omni.py to display summary from log file
# -----------------------------------------------------
Write-Host "`n[3] Updating omni.py summary printing..." -ForegroundColor Yellow

$omniPath = "omni.py"
$omni = Get-Content $omniPath -Raw

$summaryBlock = @'
        print("\\n===== SortEngine Summary =====\\n")
        log = getattr(eng, "log_file", None)
        if log:
            print(open(log, "r", encoding="utf8").read())
        else:
            print("[WARN] SortEngine did not produce a log file.")
'@

$omni = $omni -replace "eng.run\(args.input\)", "eng.run(args.input)\n$summaryBlock"

Write-WithBackup -Path $omniPath -Content $omni

# -----------------------------------------------------
# 4) Replace Automount with non-recursive version
# -----------------------------------------------------
Write-Host "`n[4] Installing Automount Safe Loader..." -ForegroundColor Yellow

$autoPath = "v2_core/system/automount/automount.py"

$autoCode = @'
"""
AutoMount V4 - Safe Loader (No Recursion)
Loads engines → plugins → system modules cleanly.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def mount_all():
    base = ROOT / "v2_core"

    registry = {
        "engines": {},
        "plugins": {},
        "system": {}
    }

    # Engines
    engines_dir = base / "engines"
    if engines_dir.exists():
        for file in engines_dir.rglob("*.py"):
            if file.name in ["__init__.py"]:
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                registry["engines"][mod.REGISTER["name"]] = mod

    # Plugins
    plugins_dir = base / "plugins"
    if plugins_dir.exists():
        for file in plugins_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                registry["plugins"][mod.REGISTER["name"]] = mod

    # System
    system_dir = base / "system"
    if system_dir.exists():
        for file in system_dir.rglob("*.py"):
            if file.name in ["__init__.py", "automount.py"]:
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                registry["system"][mod.REGISTER["name"]] = mod

    return registry
'@

Write-WithBackup -Path $autoPath -Content $autoCode

# -----------------------------------------------------
# 5) Validation Scan
# -----------------------------------------------------
Write-Host "`n[5] Running validation scan..." -ForegroundColor Yellow

$dirs = @(
    "v2_core/engines/sorter",
    "v2_core/system",
    "v2_core/system/logger"
)

foreach ($d in $dirs) {
    Write-Host "Checking $d ..." -ForegroundColor DarkCyan
    Get-ChildItem $d
}

Write-Host "`n=== DONE! V2 Logging System Installed ===" -ForegroundColor Green
Write-Host "Next: run → python omni.py sort --input sample_input --simulate" -ForegroundColor Cyan
