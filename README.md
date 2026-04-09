# InteliOmniSorter

InteliOmniSorter is a safety-first smart sorting framework for organizing files without destructive actions.

## Repository layout

- `legacy_v1/` — preserved legacy engine
- `v2_core/` — modern modular core
- `docs/` — project documentation and prompts
- root scripts — migration, scaffolding, and controller utilities

## Current direction

OMNI is being rebuilt as a controlled, reversible, auditable sorting system.

Core philosophy:

**Sort everything. Break nothing. Always recoverable.**

## Current safety rules

- dry-run first
- no overwrite
- full logging
- reversible operations
- Git-aware protection
- protected zones
- no silent behavior

## Status

See:
- `CURRENT_STATE.md`
- `CHANGELOG.md`
- `docs/MASTER_PROMPT_v0_4.md`
- `docs/SYSTEM_STATUS_v0_4.md`

## License

MIT
