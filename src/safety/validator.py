from __future__ import annotations

from pathlib import Path

from src.logger.json_logger import append_json_log, build_event
from src.safety.git_guard import build_git_protection_map, get_git_protection_for_path
from src.safety.protected_zones import is_in_protected_zone, load_registry


def validate_plan(plan_result: dict) -> dict:
    validated_items = []

    safe_count = 0
    conflict_count = 0
    blocked_count = 0

    git_map = build_git_protection_map(plan_result["scan_path"])
    registry = load_registry()

    for item in plan_result["plan"]:
        destination = Path(item["destination"])

        # 🔴 PROTECTED ZONES FIRST
        protected, reason = is_in_protected_zone(item["source"], registry)
        if protected:
            validated = {
                **item,
                "safe": False,
                "status": "blocked",
                "reason": reason,
                "blocked_by": "protected_zone",
            }
            blocked_count += 1

        # 🔴 GIT SAFETY
        elif (git := get_git_protection_for_path(item["source"], git_map)) is not None:
            validated = {
                **item,
                "safe": False,
                "status": "blocked",
                "reason": git["reason"],
                "blocked_by": "git",
            }
            blocked_count += 1

        # 🔴 DESTINATION CONFLICT
        elif destination.exists():
            validated = {
                **item,
                "safe": False,
                "status": "conflict",
                "reason": "destination already exists",
                "blocked_by": "destination_conflict",
            }
            conflict_count += 1

        # 🟢 SAFE
        else:
            validated = {
                **item,
                "safe": True,
                "status": "safe",
                "reason": "",
                "blocked_by": "",
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
        "protected_zones": registry,
    }

    log_validation(result)
    return result


def log_validation(validation_result: dict):
    append_json_log(
        "validation_log.json",
        build_event(
            "plan_validated",
            {
                "safe": validation_result["safety_summary"]["safe"],
                "blocked": validation_result["safety_summary"]["blocked"],
            },
        ),
    )


def run_validation(plan_result: dict) -> dict:
    return validate_plan(plan_result)
