# Migration Notes â€” From SmartSorter Pro V1 to InteliOmniSorter V2

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
