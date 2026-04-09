# OMNI — InteliOmniSorter
## MASTER PROMPT v0.4
### SYSTEM INTEGRITY PHASE

## 1. PROJECT IDENTITY

OMNI is a modular, safety-first intelligent file sorting system.

Core philosophy:

Sort everything. Break nothing. Always recoverable.

OMNI is not a script. It is a controlled system for understanding, organizing, and safely managing files.

---

## 2. CORE PRINCIPLES

- No destructive actions
- Dry-run is default
- Full logging
- Reversible actions
- AI suggests, never executes
- No silent behavior
- Full transparency

---

## 3. V0 SCOPE

### Included
- Folder scanning
- File metadata listing
- Basic classification
- Rules-based planning
- Validation layer
- Dry-run suggestions
- CLI interface
- Logging
- Safety layer
- Git-aware protection

### Excluded
- AI classification
- Face recognition
- Duplicate detection
- Automation without review
- Background autonomous execution

---

## 4. CORE FLOW

User → Intent → Scan → Plan → Validate → Review → Approve → Log

---

## 5. ARCHITECTURE

Modules:

- ingest
- classify
- rules
- actions
- safety
- logger
- terminal

---

## 6. SAFETY SYSTEM

- Dry-run enforced
- No overwrites
- Conflict detection
- File existence checks
- Git protection layer
- User confirmation required
- Undo capability (planned)
- Backup support (future)

---

## 7. LOGGING

All actions must be recorded with:

- source
- destination
- timestamp
- rule
- result

---

## 8. DEVELOPMENT RULES

- Git required from day one
- Changelog tracking mandatory
- Modular file structure enforced
- No untracked scripts
- Git state must be respected at runtime
- No file actions allowed on protected Git states
- All scans must include Git awareness

---

## 9. VERSION CONTROL SAFETY

OMNI must detect and respect version control systems.

If a Git repository is detected:

- Untracked files must NOT be moved
- Modified files must NOT be moved
- Staged files must NOT be moved

OMNI must report:

[OMNI] Git protection active.
[OMNI] Skipped: X files (untracked/modified/staged)

Overrides must require explicit user confirmation.

OMNI must never interfere with repository integrity.

---

## 10. FINAL DIRECTIVE

OMNI observes first.
OMNI suggests second.
OMNI executes only when safe and approved.
