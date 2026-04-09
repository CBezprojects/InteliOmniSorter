from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def ensure_log_dir(log_dir: str = "logs") -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def append_json_log(filename: str, entry: dict[str, Any], log_dir: str = "logs") -> Path:
    base = ensure_log_dir(log_dir)
    log_path = base / filename

    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = [existing]
        except Exception:
            existing = []
    else:
        existing = []

    existing.append(entry)
    log_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    return log_path


def build_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data,
    }
