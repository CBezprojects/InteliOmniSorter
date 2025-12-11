# InteliOmniSorter Changelog


## [2025-12-11 02:09] Phase 5 - Rule Engine Architecture Added

### Added
- Introduced **RuleEngine** under 2_core/system/rules/.
- Added dynamic rule loading via ules.json.
- Implemented multi-condition rule matching (type, ext, faces, camera).
- Added fallback sort logic for undefined rule matches.
- Created 2_core/config/rules.json with default rule set.
- Added support structure for profile-based sorting (config/profiles/).

### Improved
- Prepared system for PHASE 6: SortEngine ? RuleEngine integration.
- Ensured Automount V2 automatically registers the Rule Engine.

---
## [2025-12-11 02:15] Phase 6 - SortEngine ? RuleEngine Full Integration

### Added
- SortEngine now loads RuleEngine dynamically via Automount V2.
- Template expansion system ({year}, {month}, {ext}, {day}).
- Rule-based destination resolution.
- Automatic fallback sorting when no rules match.
- Updated tag classification (faces, timestamps, ext, type).

### Improved
- SortEngine pipeline fully modular and rule-driven.
- Increased compatibility with upcoming Phase 7 Rollback Engine.

---
## [2025-12-11 02:18] Phase 7 - Rollback Engine Added

### Added
- Implemented **RollbackEngine** under \2_core/system/rollback/\.
- Supports preview mode, full restore mode, and JSON rollback tracking.
- Designed for SortEngine integration (Phase 8).
- Automount-ready with REGISTER block.

---
## [2025-12-11 02:20] Phase 8 - SortEngine Rollback Integration

### Added
- SortEngine now records rollback entries for every file move.
- Automatic detection of RollbackEngine through Automount V2.
- Rollback now fully operational after any sort session.

---
