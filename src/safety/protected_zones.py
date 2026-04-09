from __future__ import annotations

import fnmatch
import json
from pathlib import Path


def load_registry() -> dict:
    config_path = Path("config/registry.json")
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def is_in_protected_zone(path: str | Path, registry: dict) -> tuple[bool, str]:
    p = Path(path)
    parts = set(p.parts)

    for zone in registry.get("protected_zones", []):
        if zone in parts:
            return True, f"protected zone: {zone}"

    name = p.name
    for pattern in registry.get("protected_patterns", []):
        if fnmatch.fnmatch(name, pattern):
            return True, f"protected pattern: {pattern}"

    return False, ""
