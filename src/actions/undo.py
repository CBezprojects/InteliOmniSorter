from __future__ import annotations

import shutil
from pathlib import Path

from src.actions.ledger import load_ledger, save_ledger


def get_latest_applied_batch():
    ledger = load_ledger()
    if not ledger:
        return None

    for batch in reversed(ledger):
        if batch.get("mode") == "applied":
            return batch

    return None


def undo_batch(batch: dict):
    reverted = 0
    skipped = 0
    failed = 0

    for item in reversed(batch.get("items", [])):
        if item.get("execution_status") != "applied":
            continue

        src = Path(item["source"])
        dst = Path(item["destination"])

        try:
            if not dst.exists():
                skipped += 1
                item["undo_status"] = "skipped_missing_destination"
                continue

            src.parent.mkdir(parents=True, exist_ok=True)

            if src.exists():
                skipped += 1
                item["undo_status"] = "skipped_source_exists"
                continue

            shutil.move(str(dst), str(src))
            reverted += 1
            item["undo_status"] = "reverted"

        except Exception as exc:
            failed += 1
            item["undo_status"] = f"failed: {exc}"

    batch["undo_summary"] = {
        "reverted": reverted,
        "skipped": skipped,
        "failed": failed,
    }

    batch["mode"] = "undone"
    batch["undone"] = True

    save_ledger([batch])
    return batch


def undo_last_batch():
    batch = get_latest_applied_batch()
    if batch is None:
        return None
    return undo_batch(batch)
