# InteliOmniSorter — Current State Snapshot

📍 Location:
C:\Users\27646\OneDrive\Master_Cloud\CleanRoot

📦 Git Status:
Pre-refactor, pre-move, broken snapshot preserved intentionally.

---

## ✅ What EXISTS

### Core
- omni.py CLI entry point
- v2_core folder structure present
- engines/, system/, automount/ scaffolding exists

### Engines
- sorter/sort_engine.py exists
- REGISTER metadata present
- SortEngine class implemented (Phase 6 logic)

### System
- Automount V2/V3 experiments exist
- Dynamic module loader via importlib.util

### PowerShell
- Terminal session recorder experiments exist
- Output logging to timestamped files partially working

---

## ⚠️ What is BROKEN (by design at this snapshot)

- Automount recursion loop
- SortEngine calls mount_all() at import time
- Automount loads SortEngine, causing infinite recursion
- Engine discovery fails due to recursive import
- Root path confusion after OneDrive restore
- Terminal recorder scripts inconsistent / experimental

---

## 🎯 Why this snapshot exists

- Preserve work before architectural correction
- Enable clean refactor without fear
- Provide reference state for Doctor diagnostics
- Freeze OneDrive-restored chaos before moving to C:\Dev

---

## ⛔ What NOT to do on this snapshot

- Do NOT fix automount here
- Do NOT move folders yet
- Do NOT clean logs aggressively
- Do NOT refactor engine imports

This snapshot is a **historical anchor**, not a fix target.
