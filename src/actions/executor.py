from __future__ import annotations

import shutil
from pathlib import Path

from src.actions.ledger import load_ledger, save_ledger
from src.logger.json_logger import append_json_log, build_event


def confirm_apply(batch_id: str, total_files: int) -> bool:
    print(f"[OMNI] Ready to apply batch: {batch_id}")
    print(f"[OMNI] Total actions to execute: {total_files}")
    response = input("[OMNI] Confirm apply? (yes/no): ").strip().lower()
    return response == "yes"


def _find_batch(batch_id: str) -> dict | None:
    ledger = load_ledger()
    for batch in ledger:
        if batch["batch_id"] == batch_id:
            return batch
    return None


def _save_batch(updated_batch: dict) -> None:
    ledger = load_ledger()
    for index, batch in enumerate(ledger):
        if batch["batch_id"] == updated_batch["batch_id"]:
            ledger[index] = updated_batch
            save_ledger(ledger)
            return
    ledger.append(updated_batch)
    save_ledger(ledger)


def apply_batch(batch_id: str) -> dict:
    batch = _find_batch(batch_id)
    if batch is None:
        raise ValueError(f"Batch not found: {batch_id}")

    if batch.get("mode") != "dry-run":
        raise ValueError(f"Batch is not a dry-run batch: {batch_id}")

    applied = 0
    blocked = 0
    failures = 0

    for item in batch["items"]:
        source = Path(item["source"])
        destination = Path(item["destination"])

        if not item.get("will_move", False):
            item["execution_status"] = "blocked"
            item["execution_reason"] = item.get("reason", "not eligible for move")
            blocked += 1
            continue

        if item.get("status") != "safe":
            item["execution_status"] = "blocked"
            item["execution_reason"] = item.get("reason", "validation did not mark file as safe")
            blocked += 1
            continue

        if not source.exists():
            item["execution_status"] = "failed"
            item["execution_reason"] = "source missing"
            failures += 1
            continue

        if destination.exists():
            item["execution_status"] = "blocked"
            item["execution_reason"] = "destination already exists at execution time"
            blocked += 1
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            item["execution_status"] = "applied"
            item["execution_reason"] = ""
            applied += 1
        except Exception as exc:
            item["execution_status"] = "failed"
            item["execution_reason"] = str(exc)
            failures += 1

    batch["mode"] = "applied"
    batch["execution_summary"] = {
        "applied": applied,
        "blocked": blocked,
        "failed": failures,
        "total": len(batch["items"]),
    }

    log_path = append_json_log(
        "action_log.json",
        build_event(
            "apply_executed",
            {
                "batch_id": batch["batch_id"],
                "scan_path": batch["scan_path"],
                "applied": applied,
                "blocked": blocked,
                "failed": failures,
            },
        ),
    )

    batch["execution_log"] = str(log_path)
    _save_batch(batch)
    return batch
