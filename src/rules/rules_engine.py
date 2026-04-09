from __future__ import annotations

from collections import Counter
from pathlib import Path

from src.logger.json_logger import append_json_log, build_event

DEFAULT_RULES = {
    "image": "Images",
    "document": "Documents",
    "archive": "Archives",
    "audio": "Audio",
    "video": "Video",
    "code": "Code",
    "unknown": "Unknown",
}

SUBTYPE_MAP = {
    # code
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".json": "json",
    ".toml": "config",
    ".yaml": "config",
    ".yml": "config",
    ".xml": "config",
    ".sh": "shell",
    ".ps1": "powershell",
    # docs
    ".md": "markdown",
    ".txt": "text",
    ".pdf": "pdf",
    ".docx": "word",
    ".xlsx": "spreadsheet",
    ".csv": "spreadsheet",
    # images
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".webp": "webp",
    ".svg": "vector",
    # archives
    ".zip": "zip",
    ".7z": "7z",
    ".rar": "rar",
}


def is_hidden_file(file_record: dict) -> bool:
    return file_record.get("name", "").startswith(".")


def get_subtype(file_record: dict) -> str:
    suffix = file_record.get("suffix", "").lower()
    if is_hidden_file(file_record):
        return "hidden"
    if not suffix:
        return "misc"
    return SUBTYPE_MAP.get(suffix, suffix.removeprefix(".") or "misc")


def suggest_destination(file_record: dict, base_path: str) -> dict:
    category = file_record.get("category", "unknown")
    target_root = DEFAULT_RULES.get(category, "Unknown")
    subtype = get_subtype(file_record)

    if category == "unknown" and is_hidden_file(file_record):
        destination = Path(base_path) / "Review" / "Hidden" / file_record["name"]
    else:
        destination = Path(base_path) / target_root / subtype / file_record["name"]

    return {
        "source": file_record["path"],
        "name": file_record["name"],
        "category": category,
        "subtype": subtype,
        "destination": str(destination),
    }


def summarize_plan(plan: list[dict]) -> dict:
    category_counts = Counter()
    subtype_counts = Counter()

    for item in plan:
        category_counts[item["category"]] += 1
        subtype_counts[f"{item['category']}::{item['subtype']}"] += 1

    return {
        "by_category": dict(sorted(category_counts.items())),
        "by_subtype": dict(sorted(subtype_counts.items())),
    }


def build_plan(scan_result: dict) -> dict:
    base_path = scan_result["scan_path"]

    plan = []
    for file_record in scan_result["files"]:
        plan.append(suggest_destination(file_record, base_path))

    summary = summarize_plan(plan)

    return {
        "scan_path": base_path,
        "total_files": len(plan),
        "summary": summary,
        "plan": plan,
    }


def log_plan(plan_result: dict) -> Path:
    event = build_event(
        "plan_generated",
        {
            "scan_path": plan_result["scan_path"],
            "total_files": plan_result["total_files"],
            "summary": plan_result["summary"]["by_category"],
        },
    )
    return append_json_log("plan_log.json", event)


def run_plan(scan_result: dict) -> dict:
    result = build_plan(scan_result)
    log_plan(result)
    return result
