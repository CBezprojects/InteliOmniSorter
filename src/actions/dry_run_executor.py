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
            }
        else:
            action = {
                **item,
                "action": "blocked",
                "mode": "dry-run",
                "will_create_dir": False,
                "will_move": False,
            }

        actions.append(action)

    return {
        "scan_path": validation_result["scan_path"],
        "total_files": validation_result["total_files"],
        "summary": validation_result["summary"],
        "safety_summary": validation_result["safety_summary"],
        "git_protection": validation_result["git_protection"],
        "directory_plan": sorted(mkdirs),
        "actions": actions,
    }


def log_dry_run(action_result: dict) -> Path:
    event = build_event(
        "dry_run_generated",
        {
            "scan_path": action_result["scan_path"],
            "total_files": action_result["total_files"],
            "safe": action_result["safety_summary"]["safe"],
            "conflicts": action_result["safety_summary"]["conflicts"],
            "blocked": action_result["safety_summary"]["blocked"],
            "git_active": action_result["git_protection"]["active"],
            "directories_planned": len(action_result["directory_plan"]),
        },
    )
    return append_json_log("action_log.json", event)


def run_dry_run(validation_result: dict) -> dict:
    result = build_dry_run_actions(validation_result)
    log_dry_run(result)
    batch = record_batch(result)
    result["batch_id"] = batch["batch_id"]
    return result
