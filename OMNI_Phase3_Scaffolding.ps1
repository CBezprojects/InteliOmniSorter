# ============================================================
# OMNI_Phase3_Scaffolding.ps1
# InteliOmniSorter V2 Core - Phase 3 Scaffolding
# - Creates v2_core folder structure
# - Writes placeholder Python modules
# - Creates OMNI controller
# - Uses existing Post-Phase Hook (which runs Git Guardian)
# ============================================================

Write-Host "=== OMNI Phase 3 - V2 Core Scaffolding ==="

# ----------------------------
# Detect repo root
# ----------------------------
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot
Write-Host "[OK] Repo root: $RepoRoot"

# ----------------------------
# Folder structure
# ----------------------------
$Folders = @(
    "v2_core",
    "v2_core/config",
    "v2_core/engines",
    "v2_core/engines/faces",
    "v2_core/engines/sorter",
    "v2_core/system",
    "v2_core/system/loader",
    "v2_core/system/doctor",
    "v2_core/system/automount",
    "v2_core/system/git_tools",
    "v2_core/system/updater",
    "v2_core/system/hooks",
    "v2_core/gui",
    "v2_core/logs",
    "v2_core/temp"
)

foreach ($f in $Folders) {
    if (!(Test-Path $f)) {
        New-Item -ItemType Directory -Path $f -Force | Out-Null
        Write-Host "[CREATE] $f"
    } else {
        Write-Host "[EXISTS] $f"
    }
}

# ----------------------------
# Helper: write file as ASCII
# ----------------------------
function Write-ModuleFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $dir = Split-Path -Parent $Path
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $Content | Out-File -FilePath $Path -Encoding ASCII -Force
    Write-Host "[WRITE] $Path"
}

# ----------------------------
# config.py
# ----------------------------
$ConfigPy = @'
# InteliOmniSorter V2 - Configuration

config = {
    "version": "2.0-core",
    "log_path": "v2_core/logs",
    "temp_path": "v2_core/temp",
    "faces_model_path": "v2_core/engines/faces",
    "sort_rules_path": "v2_core/engines/sorter"
}
'@
Write-ModuleFile "v2_core/config/config.py" $ConfigPy

# ----------------------------
# module_loader.py
# ----------------------------
$ModuleLoaderPy = @'
# InteliOmniSorter V2 - Manual module loader

import importlib.util
import os

def load_module_from_path(path, module_name):
    if not os.path.exists(path):
        print("Loader error: path does not exist:", path)
        return None

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print("Loader error:", e)
        return None
'@
Write-ModuleFile "v2_core/system/loader/module_loader.py" $ModuleLoaderPy

# ----------------------------
# doctor.py
# ----------------------------
$DoctorPy = @'
# InteliOmniSorter V2 - Doctor (self-check system)

import os

REQUIRED_FOLDERS = [
    "v2_core",
    "v2_core/logs",
    "v2_core/temp",
    "v2_core/system",
    "v2_core/engines",
    "v2_core/gui"
]

def run_basic_checks():
    print("Doctor: running basic checks...")
    missing = []
    for folder in REQUIRED_FOLDERS:
        if not os.path.exists(folder):
            missing.append(folder)
    if missing:
        print("Doctor: missing folders:")
        for m in missing:
            print(" -", m)
    else:
        print("Doctor: all required folders exist.")
'@
Write-ModuleFile "v2_core/system/doctor/doctor.py" $DoctorPy

# ----------------------------
# automount.py
# ----------------------------
$AutomountPy = @'
# InteliOmniSorter V2 - Automount placeholder

def detect_devices():
    print("Automount: device scan placeholder.")
    return []

def run_automount_cycle():
    devices = detect_devices()
    print("Automount: found", len(devices), "devices (placeholder).")
'@
Write-ModuleFile "v2_core/system/automount/automount.py" $AutomountPy

# ----------------------------
# faces_engine.py
# ----------------------------
$FacesEnginePy = @'
# InteliOmniSorter V2 - Faces engine placeholder
# Real implementation will use face_recognition and clustering.

def analyze_image(path):
    print("FacesEngine: placeholder analysis for", path)
    return None
'@
Write-ModuleFile "v2_core/engines/faces/faces_engine.py" $FacesEnginePy

# ----------------------------
# sort_engine.py
# ----------------------------
$SortEnginePy = @'
# InteliOmniSorter V2 - Sort engine placeholder
# Real implementation will handle EXIF, rules, safe moves, and logging.

def classify_file(path):
    print("SortEngine: placeholder classify for", path)
    return "unsorted"

def sort_file(path):
    category = classify_file(path)
    print("SortEngine: would move", path, "to category:", category)
'@
Write-ModuleFile "v2_core/engines/sorter/sort_engine.py" $SortEnginePy

# ----------------------------
# git_tools.py (Python wrapper calling InteliGitGuardian.ps1)
# ----------------------------
$GitToolsPy = @'
# InteliOmniSorter V2 - Git tools wrapper

import os
import subprocess

def run_git_guardian():
    repo_root = os.getcwd()
    guardian = os.path.join(repo_root, "InteliGitGuardian.ps1")
    if os.path.exists(guardian):
        print("GitTools: running Git Guardian...")
        subprocess.call(["powershell", "-ExecutionPolicy", "Bypass", "-File", guardian])
    else:
        print("GitTools: InteliGitGuardian.ps1 not found.")
'@
Write-ModuleFile "v2_core/system/git_tools/git_tools.py" $GitToolsPy

# ----------------------------
# gui_main.py
# ----------------------------
$GuiMainPy = @'
# InteliOmniSorter V2 - GUI placeholder
# Future: Tkinter GUI implementation

def start_gui():
    print("OMNI GUI placeholder. Future Tkinter interface goes here.")

if __name__ == "__main__":
    start_gui()
'@
Write-ModuleFile "v2_core/gui/gui_main.py" $GuiMainPy

# ----------------------------
# OMNI_Controller.ps1
# ----------------------------
$OmniControllerPs1 = @'
param(
    [string]$Phase = "Unknown Phase"
)

Write-Host "=== OMNI Controller ==="
Write-Host "Executing Phase: $Phase"

# Placeholder for future per-phase logic
switch ($Phase) {
    "V2 Scaffolding" {
        Write-Host "Phase action: V2 scaffolding already created by OMNI_Phase3_Scaffolding.ps1"
    }
    default {
        Write-Host "No specific action defined for this phase yet."
    }
}

# Call post-phase hook if available
$HookPath = "v2_core/system/hooks/post_phase.ps1"
if (Test-Path $HookPath) {
    powershell -ExecutionPolicy Bypass -File $HookPath -PhaseName $Phase
} else {
    Write-Host "Post-Phase hook not found at: $HookPath"
}
'@
Write-ModuleFile "OMNI_Controller.ps1" $OmniControllerPs1

# ----------------------------
# Ensure post_phase.ps1 exists (do not overwrite if already present)
# ----------------------------
$PostPhasePath = "v2_core/system/hooks/post_phase.ps1"

if (!(Test-Path $PostPhasePath)) {
    $PostPhasePs1 = @'
param(
    [string]$PhaseName = "Unknown Phase"
)

Write-Host "=== OMNI Post-Phase Hook ==="
Write-Host "Phase completed: $PhaseName"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$GuardianPath = Join-Path $RepoRoot "InteliGitGuardian.ps1"

if (Test-Path $GuardianPath) {
    powershell -ExecutionPolicy Bypass -File $GuardianPath
} else {
    Write-Host "Git Guardian not found at: $GuardianPath"
}
'@
    Write-ModuleFile $PostPhasePath $PostPhasePs1
} else {
    Write-Host "[INFO] Existing post_phase.ps1 detected; leaving it unchanged."
}

Write-Host "=== OMNI Phase 3 Scaffolding COMPLETE ==="
Write-Host "You can now run: powershell -ExecutionPolicy Bypass -File .\OMNI_Controller.ps1 -Phase 'V2 Scaffolding'"

