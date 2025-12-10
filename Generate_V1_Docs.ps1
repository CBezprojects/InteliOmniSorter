# ============================================================
# Generate_V1_Docs.ps1
# Creates all 9 documentation files for SmartSorter Pro V1
# Writes them into legacy_v1/docs/
# ============================================================

Write-Host "Creating V1 Documentation..." -ForegroundColor Cyan

# Ensure docs folder exists
$docsPath = "legacy_v1/docs"
if (!(Test-Path $docsPath)) {
    New-Item -ItemType Directory -Path $docsPath -Force | Out-Null
}

# Helper function to write a file
function Write-DocFile {
    param(
        [string]$Path,
        [string]$Content
    )
    $Content | Out-File -FilePath $Path -Encoding UTF8 -Force
    Write-Host "Generated: $Path" -ForegroundColor Green
}

# ------------------------------------------
# 1. V1_History.md
# ------------------------------------------
$V1_History = @"
# SmartSorter Pro — V1 History

SmartSorter began as a personal automation tool designed to solve a practical problem:
sorting thousands of photos, screenshots, downloads, and mixed-format files distributed
across multiple drives. Over time, the tool evolved into a semi-modular system with
PowerShell automation, Python-based logic, and a set of convenience scripts created
incrementally to handle real-world file chaos.

V1 was not designed upfront as a unified product. It grew reactively, responding to
day-by-day needs:

- Clean a folder with 10 000+ mixed files
- Sort images by date and similarity
- Create structured destination folders
- Track which files moved where
- Keep logs for reversibility
- Add optional face detection
- Add auto-mount for phones and USB devices
- Run the pipeline from a single script

As the capabilities increased, SmartSorter Pro V1 became a hybrid system:

- PowerShell (for automation, scanning, logging)
- Python (for face detection & similarity clustering)
- dlib / face_recognition (for embeddings)
- SQLite (for temporary file metadata storage)
- CSV logs for tracking each run

By late V1, the system was powerful—but fragmented, inconsistent, and difficult to extend.

The decision was made to freeze V1 and create InteliOmniSorter V2, a unified,
modular, modern version that inherits the ideas but not the legacy complexity.
"@

Write-DocFile "$docsPath/V1_History.md" $V1_History

# ------------------------------------------
# 2. V1_What_Was_Accomplished.md
# ------------------------------------------
$V1_Accomplished = @"
# SmartSorter Pro V1 — What Was Accomplished

V1 was ultimately successful in its primary mission: transforming large, chaotic file
collections into structured, organized, searchable libraries.

Major accomplishments:

### 1. Automated File Sorting Pipeline
Users could drop thousands of mixed-format files into a folder and run a single script
to have SmartSorter organize them by type, extension, date, and customizable rules.

### 2. Face Detection & Face-Based Clustering
The Python module allowed optional facial embedding extraction and basic similarity
labels, enabling grouping of images by the people in them.

### 3. Logging & Traceability
Every file move was logged into CSV files, making every operation reversible.
This was crucial for safety.

### 4. Integration With Auto-Mounting
The system could automatically detect a mounted phone or USB device and begin ingesting
and sorting its contents.

### 5. Semi-GUI via PowerShell Menus
While primitive, the script-based interface allowed users to select run modes,
configure settings, and monitor progress.

### 6. Cross-Platform Ideas
Although mostly Windows-first, V1 hinted at an architecture that could eventually work
on Linux or macOS.

### 7. A Knowledge Base for V2
V1 provided the insight needed to design a modern, unified, maintainable system.
"@

Write-DocFile "$docsPath/V1_What_Was_Accomplished.md" $V1_Accomplished

# ------------------------------------------
# 3. V1_Architecture.md
# ------------------------------------------
$V1_Architecture = @"
# SmartSorter Pro V1 — Architecture Overview

V1 architecture consisted of loosely connected modules and scripts without a unified
framework. It worked, but lacked cohesion and scalability.

## 1. PowerShell Automation Layer
- Entry point for running the sorter
- Folder scanning
- Routing logic
- Logging
- Menu display

## 2. Python Processing Layer
- face_recognition + dlib embeddings
- Facial similarity clustering
- Lightweight sort engine
- SQLite temporary DB

## 3. File Classification Logic
Sorting was based on:
- Extension
- MIME type
- Date created/modified
- EXIF metadata
- Optional faces

## 4. Logging System
- CSV logs per run
- Reversible operations

## 5. Auto-Mount System
- Polling-based detection
- Pulls from DCIM or removable storage

## 6. Face Engine
- Embedding extraction
- Euclidean distance similarity

---

## Architectural Issues
- No plugin system
- Tight coupling between PowerShell & Python
- Hard to package
- No GUI framework
- Inconsistent folder structure
"@

Write-DocFile "$docsPath/V1_Architecture.md" $V1_Architecture

# ------------------------------------------
# 4. V1_Limitations.md
# ------------------------------------------
$V1_Limitations = @"
# SmartSorter Pro V1 — Limitations

## 1. Not Modular
Logic was spread across scripts without separation of concerns.

## 2. Large Binary Dependencies
dlib and wheels could not be committed to GitHub.

## 3. Scattered Sorting Logic
Routing rules existed in multiple places.

## 4. No Automatic Rollback
Logs existed, but no built-in undo system.

## 5. Primitive Auto-Mount
Unreliable polling method.

## 6. Script-Based Interface
No GUI toolkit.

## 7. Difficult Packaging
Mixed PowerShell and Python.

## 8. Windows-Only
Pathing and dependencies were not cross-platform.

These limitations shaped V2’s modular redesign.
"@

Write-DocFile "$docsPath/V1_Limitations.md" $V1_Limitations

# ------------------------------------------
# 5. V1_Features.md
# ------------------------------------------
$V1_Features = @"
# SmartSorter Pro V1 — Feature List

## Core Features
- Automated file sorting
- EXIF date sorting
- Extension-based routing
- Similar-face clustering
- Optional face recognition module
- CSV logs for every operation

## Automation Features
- Auto-mount detection
- Batch processing
- One-click ingest

## User Interface
- Menu-driven script interface
- Progress output
- Logging summary

## Safety
- Avoids overwriting
- Reversible via logs

## Developer Tools
- Python embedding modules
- PowerShell orchestration
- SQLite scratch DB
"@

Write-DocFile "$docsPath/V1_Features.md" $V1_Features

# ------------------------------------------
# 6. V1_Database_Structure.md
# ------------------------------------------
$V1_DB = @"
# SmartSorter Pro V1 — Database Structure

V1 used a temporary SQLite database for metadata storage.

## Table: faces
- id (INTEGER)
- file_path (TEXT)
- embedding (BLOB)
- created_at (TEXT)

## Table: files
- id (INTEGER)
- file_path (TEXT)
- hash (TEXT)
- type (TEXT)
- date_taken (TEXT)

This DB will be redesigned in V2 as a pluggable provider.
"@

Write-DocFile "$docsPath/V1_Database_Structure.md" $V1_DB

# ------------------------------------------
# 7. V1_SortLogic.md
# ------------------------------------------
$V1_SortLogic = @"
# SmartSorter Pro V1 — Sorting Logic Overview

Sorting followed a sequential decision chain:

## 1. Identify File Type
Based on extension/MIME.

## 2. Extract Metadata
EXIF timestamps, device model, orientation.

## 3. Compute Destination Folder
Examples:
- Images → Photos/YYYY/MM-DD
- Videos → Videos/YYYY/MM-DD
- Screenshots → Screenshots/YYYY-MM
- Documents → Documents/
- Unknown → Misc/

## 4. Apply Optional Face Clustering
Distance thresholds:
- <0.45 → same person
- 0.45–0.6 → maybe
- >0.6 → different

## 5. Move Files Safely
Ensures no overwrites.

## 6. Write Logs
CSV logs allow reversibility.

This becomes the foundation for V2’s `sort_engine.py`.
"@

Write-DocFile "$docsPath/V1_SortLogic.md" $V1_SortLogic

# ------------------------------------------
# 8. V1_Codebase_Map.md
# ------------------------------------------
$V1_CodeMap = @"
# SmartSorter Pro V1 — Codebase Map

legacy_v1/
├── src/
│   └── _SmartSorter/
│       ├── sorter.py
│       ├── smartbrain.py
│       ├── smartbrain.db
│       ├── SmartSorter_Run.ps1
│       ├── SmartBrain_Install.ps1
│       ├── dlib-19.24.1.whl
│       └── misc scripts...
├── logs/
│   └── _SortLogs/
└── docs/
    └── V1 documentation set

V1 lacked modularity; V2 introduces consistent engines, systems, GUI, and plugin loader.
"@

Write-DocFile "$docsPath/V1_Codebase_Map.md" $V1_CodeMap

# ------------------------------------------
# 9. V1_Migration_Notes.md
# ------------------------------------------
$V1_Migration = @"
# Migration Notes — From SmartSorter Pro V1 to InteliOmniSorter V2

## What Carries Over
- Core idea: automated intelligent sorting
- Facial embedding capability
- Logging philosophy
- Auto-ingest workflow
- Python-first processing

## What Changes
- PowerShell logic replaced with Python modules
- Unified CLI + GUI
- Centralized sort engine
- New face engine isolated in its own module
- Database replaced with modular provider

## Removed in V2
- dlib wheels in repo
- PowerShell launcher
- Ad-hoc menus
- Hardcoded routing rules

## V2 Goals
- Clean architecture
- Plugin system
- Self-healing (doctor)
- Cross-platform
- Better mount detection
- EXE packaging

V2 is a full redesign, not a patch.
"@

Write-DocFile "$docsPath/V1_Migration_Notes.md" $V1_Migration

Write-Host "All V1 documentation generated successfully!" -ForegroundColor Cyan
