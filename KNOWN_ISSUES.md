# Known Issues — Pre-Refactor Snapshot

## 🔁 Automount Infinite Recursion

### Symptom
- Python crashes with:
  RecursionError: maximum recursion depth exceeded

### Cause
- automount.mount_all() dynamically loads all engine modules
- sort_engine.py calls mount_all() at import time
- Automount loads sort_engine.py
- sort_engine.py immediately calls mount_all()
- Loop repeats until recursion limit is hit

### Stack Trace Pattern
- sort_engine.py → mount_all()
- automount.py → load_module(sort_engine.py)
- sort_engine.py → mount_all()
- (repeats)

### Architectural Flaw
❌ Engines should NEVER invoke automount during import  
✅ Automount must be a bootstrap phase only

---

## 📂 Path Issues

- ROOT resolved inconsistently
- v2_core/v2_core path duplication observed
- OneDrive restore caused partial rollback

---

## 🖥 Terminal Recorder Issues

- Mixed use of Start-Process and Invoke-Expression
- stdout/stderr redirect conflicts
-  null when executed inline
- Recorder not yet session-wide

---

## 🧭 Resolution Strategy (future)

- Decouple automount from engine import
- Lazy-load engines at runtime, not import time
- Introduce engine registry cache
- Rebuild Terminal Recorder as a session hook

❗ Fixes intentionally deferred to next phase.
