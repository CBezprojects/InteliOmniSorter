# InteliOmniSorter — MASTER PLAN (Unified, Trigger-Free)

**Authoritative offline-first digital hygiene system** for photos, videos, documents, and multi-device/cloud ingestion — designed to be *safe, smart, and easy to use*, and to run forever (including after migration to POP!_OS/Linux).

This file is the single source of truth for: **vision, philosophy, scope, phases, UX/GUI goals, automation, and device plans**.

---

## 1) Core Philosophy

### Offline-first, privacy-first
- Local storage is the **source of truth**
- Cloud services are **ingest sources** (one-way pull), not live dependencies
- Default behavior is **non-destructive**
- Every mutation requires **verification + rollback path**

### Registry-driven architecture (calm bootstrap)
- Discovery is centralized and executed **once at startup**
- Engines must never trigger scanning at import-time
- `omni.py` owns bootstrap and orchestration
- Clear contracts beat clever coupling

### “Smart” must be understandable
- Smart = transparent + auditable + reversible
- Every decision should be explainable:
  - *Why was this file moved?*
  - *Which rule matched?*
  - *What metadata was used?*
  - *Can I undo it?*

### Easy to use beats feature-bloat
- A non-technical user should be able to:
  - Pick sources
  - Preview results
  - Run safely
  - Search the archive
  - Undo actions
- Power-users still get CLI + logs + automation

---

## 2) Current State (Confirmed in Repo)

### Repo + branch
- Repo path: `C:\Dev\InteliOmniSorter`
- Working branch: `v2.1-refactor`

### Architecture status
- Registry contract exists: `v2_core/system/registry.py`
- Automount rewritten as discovery-only: `v2_core/system/automount/automount.py`
- `mount_all` removed; `omni.py` owns bootstrap (`discover()` called once)
- Sorter engine no longer triggers recursion at import-time

### Tooling status
- Terminal Session Recorder installed: `tools/terminal/Start-TerminalSession.ps1` and `Stop-TerminalSession.ps1`
- Backups directory exists: `v2_core/_backups`

### Known issues (active)
- RuleEngine warning: UTF-8 BOM when loading rules (needs utf-8-sig handling)
- Registry shows empty until all engines expose correct REGISTER contracts
- Sample run failure expected when input folder missing

---

## 3) Product Promise (What this becomes)

InteliOmniSorter becomes a **personal offline “data hygiene OS”** that:
- Drains cloud storage into a local archive
- Cleans phones and device sources after verification
- Organizes media + docs intelligently
- Builds a searchable index
- Runs daily/weekly automatically
- Prevents re-chaos (ongoing hygiene)

Target end-state:
- **Everything offline** except email (email stays online by design)
- Cloud accounts become empty/dormant/legacy, not the master store

---

## 4) System Layers (Mental Model)

1. **Sources** (phone, cloud exports, drives, OneDrive folders, USB cameras)
2. **Staging** (quarantine + verification area)
3. **Engines** (metadata, dedupe, faces, OCR, rules, classification)
4. **Archive** (structured offline library, stable paths)
5. **Index** (fast search across media + docs)
6. **Hygiene Loop** (incremental runs + monitoring + reporting)

Key rule:
> Nothing touches the archive unless staging verifies integrity.

---

## 5) Ingest Sources (All Planned)

### 5.1 Samsung Phone (Primary capture device)
Goals:
- Phone is a capture device, not long-term storage
- Regular pulls to staging, then optional cleanup

Planned flows:
- **USB ingest** (simple)
- **ADB ingest** (advanced, more control)
- WhatsApp media extraction + separation:
  - Images / Videos / Voice notes / Documents
- Screenshots and duplicates cleanup (post-verification)
- “Do not delete on phone” mode until confidence is high

### 5.2 Samsung Cloud
- Treated as legacy ingest
- One-time full drain + occasional audits

### 5.3 Google Photos
- Full Takeout
- Chunked ZIP handling
- Metadata reconciliation (JSON sidecars → EXIF where possible)
- Deduplication + timeline repair
End goal:
- Google Photos empty/dormant

### 5.4 Google Drive
- Full offline mirror
- Preserve folder structure
- Version hygiene:
  - Keep newest
  - Archive older to a versions folder
- Document classification + search index
End goal:
- Google Drive empty/dormant (except email ecosystem)

### 5.5 OneDrive / “Master_Cloud”
- Transitional source during migration
- Pull offline and normalize into archive
- Then reduce OneDrive to minimal or none (as desired)

### 5.6 External Drives / USB Media / Cameras
- External HDD/SSD ingestion
- Camera SD card ingestion
- NAS support later
- Multi-volume support (per-drive staging + per-drive archive)

### 5.7 Email (exception)
- Remains online
- Optional read-only local archive later
- Not part of the active hygiene loop initially

---

## 6) Engine Capabilities (Planned)

### 6.1 Media Engine (Photos)
- EXIF parsing: date, device, lens, GPS (optional)
- Timeline clustering
- Face detection/recognition (optional module)
- Event inference (lightweight, explainable)
- Duplicate detection:
  - Hash-based (fast)
  - Perceptual (optional)

### 6.2 Media Engine (Videos)
- Duration, resolution, codec, FPS
- Source grouping (WhatsApp vs camera vs screen recording)
- Duplicate detection where feasible

### 6.3 Document Engine
- File-type aware processing: PDF/DOCX/TXT/MD
- OCR for scanned PDFs (optional, staged)
- “Active vs Archive” classification:
  - Receipts, invoices, statements, ID docs
  - Work docs
  - School/academic docs
  - Manuals, guides, reference

### 6.4 Rules Engine (User-defined)
- Rules are human-readable and override “AI”
- Priority order:
  1) Explicit rules
  2) Metadata heuristics
  3) Optional intelligence modules
- Always logs:
  - rule matched
  - confidence
  - output path

---

## 7) GUI Plan (Remembered + Locked)

The GUI is not “nice-to-have” — it’s the usability layer that prevents mistakes.

### 7.1 GUI goals
- One-screen “Run a safe sort” flow
- Clear source selection (phone / cloud export / folder / drive)
- Preview before committing:
  - X files will move
  - Y duplicates found
  - Z conflicts to resolve
- “Undo last run” button
- “Dry run” toggle (simulate)

### 7.2 GUI tabs (planned)
1) **Dashboard**
   - last run summary
   - health checks
   - storage usage
2) **Sources**
   - add/edit sources (folders, removable drives, exports)
   - phone ingest wizard (later)
3) **Run**
   - run profiles (photos / docs / everything)
   - dry-run preview
   - execute + progress
4) **Review**
   - duplicates review
   - conflict resolver (same name, same hash, etc.)
5) **Search**
   - unified search across archive + docs
   - filters: date, device, people, type, tags
6) **Settings**
   - archive paths
   - staging paths
   - safety toggles
   - schedule settings (daily/weekly)
7) **Logs**
   - readable logs + “export diagnostics”

### 7.3 UX design principles
- Safety-first: destructive actions require explicit confirm
- Explainability: show “why” behind moves
- Recoverability: undo and backups are always present
- Speed: index-driven browsing, not folder-digging

---

## 8) Automation & Continuous Hygiene

### 8.1 Windows phase (current)
- Task Scheduler jobs (daily/weekly)
- Watch folders optional later
- “Incremental runs” to avoid reprocessing

### 8.2 POP!_OS / Linux phase (target)
- Cron/systemd timers
- Headless runs supported
- Same config files, same behaviors
- Paths abstracted (no hard-coded Windows separators)

Automation rules:
- No silent deletion
- Staging verification required
- Logs + summary report each run
- “Stop safely” supported (resume without corruption)

---

## 9) Safety Guarantees (Non-negotiable)

- Backups before any mutation
- Staging before archive
- Verification before cleanup
- Never delete cloud until offline integrity confirmed
- No “smart guessing” without logging and an undo path

---

## 10) De-Clouding Endgame (What “Done” Means)

Done means:
- Google Photos drained and verified offline
- Google Drive drained and verified offline
- Samsung Cloud drained and verified offline
- Phone storage reduced to short-term capture + essential apps
- Offline archive searchable and stable
- System runs daily/weekly with low maintenance

Email remains online.

---

## 11) Phased Roadmap (Master To-Do)

### Phase A — Architecture Foundation (DONE/IN PROGRESS)
- [x] Registry module exists
- [x] Discovery-only automount
- [x] Remove import-time recursion
- [x] `omni.py` bootstrap owns discover()
- [ ] Confirm engines expose correct REGISTER contracts (populate registry)
- [ ] Add “registry audit” command to show what got registered

### Phase B — Stability + Doctor (NEXT)
- [ ] Fix RuleEngine UTF-8 BOM rule loading (utf-8-sig)
- [ ] Doctor: validate environment (Python, paths, permissions)
- [ ] Doctor: validate staging/archive writable
- [ ] Doctor: validate external tools (exiftool, ffmpeg) if used
- [ ] Add consistent structured logging (JSONL optional)

### Phase C — Core Sorting (Desktop)
- [ ] Define default archive layout (photos/videos/docs)
- [ ] Implement staging workflow (copy → verify → move)
- [ ] Dedup pipeline (hash + review queue)
- [ ] Conflict resolver strategy (name collisions)
- [ ] “Dry run” fully supported with preview report
- [ ] Undo last run (transaction log)

### Phase D — Search & Index
- [ ] Build local index DB (SQLite)
- [ ] Fast search with filters
- [ ] Link search hits to file locations
- [ ] Store provenance: source, ingest date, rule applied

### Phase E — Samsung Phone Ingest
- [ ] Define phone folder map
- [ ] USB ingest wizard
- [ ] WhatsApp media pipeline
- [ ] Screenshot cleanup flow
- [ ] Optional device cleanup after verification

### Phase F — Cloud Ingest (Google)
- [ ] Google Takeout ingestion for Photos
- [ ] Metadata repair (sidecar JSON)
- [ ] Google Drive export ingestion
- [ ] Version hygiene rules

### Phase G — Continuous Hygiene
- [ ] Scheduled runs (daily/weekly)
- [ ] Incremental detection (only process new/changed)
- [ ] Watch folders (optional)
- [ ] Run summaries + notifications (local first)

### Phase H — POP!_OS Migration
- [ ] Path abstraction layer
- [ ] Cron/systemd timer configs
- [ ] Headless CLI workflows finalized
- [ ] Portable config + portable DB
- [ ] Test migration with a cloned dataset

---

## 12) Repository Conventions (Design Rules)

- `v2_core/` contains engines, system modules, and contracts
- `tools/` contains PowerShell utilities and helpers
- `logs/` stays untracked by Git unless explicitly needed
- Every “super block” change must:
  - create backups
  - be reversible
  - end with a clear test command

---

## 13) Golden Rule

If the architecture is calm, the data will follow.

