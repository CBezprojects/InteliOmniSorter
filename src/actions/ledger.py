from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

LEDGER_PATH = Path("logs/execution_ledger.json")


def ensure_ledger() -> Path:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        LEDGER_PATH.write_text("[]", encoding="utf-8")
    return LEDGER_PATH


def load_ledger() -> list[dict]:
    ensure_ledger()
    try:
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_ledger(entries: list[dict]) -> None:
    ensure_ledger()
    LEDGER_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def create_batch_record(action_result: dict) -> dict:
    batch_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    items = []
    for item in action_result["actions"]:
        items.append(
            {
                "source": item["source"],
                "destination": item["destination"],
                "category": item.get("category", "unknown"),
                "subtype": item.get("subtype", "misc"),
                "status": item.get("status", "unknown"),
                "reason": item.get("reason", ""),
                "action": item.get("action", "unknown"),
                "mode": item.get("mode", "dry-run"),
                "will_move": item.get("will_move", False),
            }
        )

    return {
        "batch_id": batch_id,
        "timestamp": timestamp,
        "mode": "dry-run",
        "scan_path": action_result["scan_path"],
        "total_files": action_result["total_files"],
        "safety_summary": action_result["safety_summary"],
        "directory_plan": action_result["directory_plan"],
        "items": items,
    }


def record_batch(action_result: dict) -> dict:
    ledger = load_ledger()
    batch = create_batch_record(action_result)
    ledger.append(batch)
    save_ledger(ledger)
    return batch


def get_latest_batch() -> dict | None:
    ledger = load_ledger()
    if not ledger:
        return None
    return ledger[-1]
