from __future__ import annotations

from pathlib import Path

from src.logger.json_logger import append_json_log, build_event
from src.safety.git_guard import build_git_protection_map, get_git_protection_for_path


def validate_plan(plan_result: dict) -> dict:
    validated_items = []

    safe_count = 0
    conflict_count = 0
    blocked_count = 0

    git_map = build_git_protection_map(plan_result["scan_path"])

    for item in plan_result["plan"]:
        destination = Path(item["destination"])
        git_protection = get_git_protection_for_path(item["source"], git_map)

        if git_protection is not None:
            validated = {
                **item,
                "safe": False,
                "status": "blocked",
                "reason": git_protection["reason"],
                "blocked_by": "git",
                "git_status": git_protection["git_status"],
            }
            blocked_count += 1

        elif destination.exists():
            validated = {
                **item,
                "safe": False,
                "status": "conflict",
                "reason": "destination already exists",
                "blocked_by": "destination_conflict",
                "git_status": "",
            }
            conflict_count += 1

        else:
            validated = {
                **item,
                "safe": True,
                "status": "safe",
                "reason": "",
                "blocked_by": "",
                "git_status": "",
            }
            safe_count += 1

        validated_items.append(validated)

    summary = {
        "safe": safe_count,
        "conflicts": conflict_count,
        "blocked": blocked_count,
    }

    result = {
        "scan_path": plan_result["scan_path"],
        "total_files": plan_result["total_files"],
        "summary": plan_result["summary"],
        "plan": validated_items,
        "safety_summary": summary,
        "git_protection": git_map,
    }

    log_validation(result)
    return result


def log_validation(validation_result: dict) -> Path:
    event = build_event(
        "plan_validated",
        {
            "scan_path": validation_result["scan_path"],
            "total_files": validation_result["total_files"],
            "safe": validation_result["safety_summary"]["safe"],
            "conflicts": validation_result["safety_summary"]["conflicts"],
            "blocked": validation_result["safety_summary"]["blocked"],
            "git_active": validation_result["git_protection"]["active"],
            "git_protected_total": validation_result["git_protection"]["summary"][
                "protected_total"
            ],
        },
    )
    return append_json_log("validation_log.json", event)


def run_validation(plan_result: dict) -> dict:
    return validate_plan(plan_result)
