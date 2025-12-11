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
