<!-- Copilot / AI Agent instructions for InteliOmniSorter -->
# InteliOmniSorter — Agent Guidance

This short guide highlights project-specific conventions, key files, and concrete examples to help an AI coding agent be productive immediately in this repo.

1) Big picture
- **Legacy V1 engine (working):** `legacy_v1/` contains the original SmartSorter written as a PowerShell automation layer orchestrating a Python processing layer (`legacy_v1/src/_SmartSorter/`), SQLite temp DB (`smartbrain.db`), and face/embedding code (`smartbrain.py`, `sorter.py`). See `legacy_v1/docs/V1_Architecture.md` and `V1_SortLogic.md` for the original design and decision chain.
- **V2 Core (scaffold):** `v2_core/` is the modern modular core. It currently holds system hooks (`v2_core/system/hooks/`). New features should live here (engines, plugin loader, packaging).

2) Languages & runtime
- Primary scripts are **PowerShell** (ASCII-safe variants) for orchestration and **Python** for image/face processing. Expect Windows-first PowerShell commands (user environment is Windows/pwsh).

3) Key files and flows (reference examples)
- Hook system: `v2_core/system/hooks/post_phase.ps1` — called after OMNI phases. Install helper: `Setup_OMNI_PostPhaseHook.ps1` (shows how to wire hooks and gives example call lines).
- Git safety: `InteliGitGuardian.ps1` — runs checks before committing/pushing. Important constraints are enforced here: max file size (~50MB) and forbidden extensions (`.zip`, `.whl`, `.mp4`, etc.). Agents should not introduce large binary blobs.
- Legacy sorter entry: `legacy_v1/src/_SmartSorter/SmartSorter_Run.ps1` and Python modules `smartbrain.py` / `sorter.py` implement sort logic and face clustering thresholds (see `V1_SortLogic.md`).
- Logs: `legacy_v1/logs/_SortLogs/` — CSV logs are used for reversible operations. Avoid destroying those when refactoring.

4) Conventions & patterns
- Scripts are written to be ASCII-safe; avoid non-ASCII characters in generated scripts and messages.
- PowerShell calling convention: use `powershell -ExecutionPolicy Bypass -File "<script>" -ParamName "Value"` (examples in `Setup_OMNI_PostPhaseHook.ps1`).
- Safety-first: any automated commit/push should respect the checks in `InteliGitGuardian.ps1`. If adding automation, call or mirror its checks.
- Sorting decision chain is deterministic and sequential (type → metadata → destination → optional face clustering → move → log). Preserve this flow when moving logic to V2.

5) Integration points & external deps
- Face engine: depends on `dlib` and `face_recognition` (legacy). A `dlib-*.whl` exists in `legacy_v1/src/_SmartSorter/` indicating a pinned wheel—avoid unexpected upgrades.
- SQLite temp DB: `legacy_v1/src/_SmartSorter/smartbrain.db` used by Python layer; preserve schema or migrate carefully (`legacy_v1/docs/V1_Database_Structure.md`).

6) Developer workflows (how to run things)
- Run legacy sorter locally (Windows PowerShell):
  - `powershell -ExecutionPolicy Bypass -File legacy_v1/src/_SmartSorter/SmartSorter_Run.ps1`
- Install post-phase hook (creates `v2_core/system/hooks/post_phase.ps1`):
  - `powershell -ExecutionPolicy Bypass -File Setup_OMNI_PostPhaseHook.ps1`
- Run Git guardian (safety checks + commit/push):
  - `powershell -ExecutionPolicy Bypass -File InteliGitGuardian.ps1`

7) What to watch for when editing
- Do not commit large media files or binary wheels; `InteliGitGuardian.ps1` will block them. Prefer referencing external artifact stores for large binaries.
- Preserve CSV log formats and the reversible moves approach in `legacy_v1/logs/_SortLogs/`.
- When refactoring sorting logic to `v2_core/`, keep the step order from `V1_SortLogic.md` and document any threshold changes (face distance thresholds are significant to end-users).
- The repository README currently contains unresolved merge markers — be cautious when editing top-level docs and resolve conflicts.

8) Example tasks an agent can safely do now
- Add a small wrapper in `v2_core/` that calls the legacy sorter and pipes its CSV logs into a `v2_core/` monitor.
- Create unit-like smoke tests that run `SmartSorter_Run.ps1` with a small test folder (do not commit test media into repo).
- Normalize `v2_core/system/hooks/post_phase.ps1` to a robust implementation that mirrors `Setup_OMNI_PostPhaseHook.ps1` template.

If something here is unclear or you'd like me to expand a section (examples, testing commands, or a migration checklist for V1→V2), tell me which part to iterate on.
