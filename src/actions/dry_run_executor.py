from __future__ import annotations

from pathlib import Path

from src.actions.ledger import record_batch
from src.logger.json_logger import append_json_log, build_event


def build_dry_run_actions(validation_result: dict) -> dict:
    actions = []
    mkdirs = set()

    for item in validation_result["plan"]:
        destination = Path(item["destination"])
        mkdirs.add(str(destination.parent))

        if item["safe"]:
            action = {
                **item,
                "action": "move",
                "mode": "dry-run",
                "will_create_dir": True,
                "will_move": True,
                "dry_run_reason": "validated safe",
            }
        else:
            action = {
                **item,
                "action": "blocked",
                "mode": "dry-run",
                "will_create_dir": False,
                "will_move": False,
                "dry_run_reason": item.get("reason", "blocked by validation"),
            }

        actions.append(action)

    return {
        "scan_path": validation_result["scan_path"],
        "total_files": validation_result["total_files"],
        "summary": validation_result["summary"],
        "safety_summary": validation_result["safety_summary"],
        "git_protection": validation_result["git_protection"],
        "mode": "dry-run",
        "actions": actions,
        "items": actions,
        "directories_to_create": sorted(mkdirs),
    }


def run_dry_run(validation_result: dict) -> dict:
    return build_dry_run_actions(validation_result)
