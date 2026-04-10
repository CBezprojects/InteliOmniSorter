from __future__ import annotations
import shutil
from pathlib import Path
from src.actions.ledger import load_ledger, save_ledger


def undo_last_batch():
    ledger = load_ledger()
    if not ledger:
        return None

    for batch in reversed(ledger):
        if batch.get("mode") == "applied":
            return _undo(batch, ledger)

    return None


def _undo(batch, ledger):
    restored = 0
    skipped = 0

    for item in batch["items"]:
        if item.get("execution_status") != "applied":
            continue

        src = Path(item["destination"])
        dst = Path(item["source"])

        if not src.exists():
            skipped += 1
            continue

        if dst.exists():
            skipped += 1
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        restored += 1

    batch["mode"] = "undone"
    batch["undo_summary"] = {"restored": restored, "skipped": skipped}

    save_ledger(ledger)
    return batch
