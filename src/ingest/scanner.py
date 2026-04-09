from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from src.classify.classifier import classify_path, summarize_categories
from src.logger.json_logger import append_json_log, build_event

DEFAULT_IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "logs",
    "reports",
}


@dataclass(slots=True)
class FileRecord:
    name: str
    path: str
    size: int
    modified: str
    suffix: str
    parent: str
    category: str


def is_ignored(path: Path, base_path: Path) -> bool:
    try:
        relative_parts = path.relative_to(base_path).parts
    except ValueError:
        return False
    return any(part in DEFAULT_IGNORED_DIRS for part in relative_parts)


def iter_files(base_path: Path) -> Iterable[Path]:
    for item in base_path.rglob("*"):
        if is_ignored(item, base_path):
            continue
        if item.is_file():
            yield item


def scan_directory(path: str) -> dict:
    base_path = Path(path).expanduser().resolve()

    if not base_path.exists():
        raise FileNotFoundError(f"[OMNI] Path does not exist: {base_path}")

    if not base_path.is_dir():
        raise NotADirectoryError(f"[OMNI] Path is not a directory: {base_path}")

    files: list[dict] = []

    for item in iter_files(base_path):
        stat = item.stat()
        classification = classify_path(item)

        record = FileRecord(
            name=item.name,
            path=str(item),
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            suffix=item.suffix.lower(),
            parent=str(item.parent),
            category=classification["category"],
        )
        files.append(asdict(record))

    result = {
        "scan_path": str(base_path),
        "file_count": len(files),
        "timestamp": datetime.now().isoformat(),
        "category_summary": summarize_categories(files),
        "files": files,
    }

    return result


def log_scan(result: dict) -> Path:
    event = build_event(
        "scan_completed",
        {
            "scan_path": result["scan_path"],
            "file_count": result["file_count"],
            "category_summary": result["category_summary"],
        },
    )
    return append_json_log("scan_log.json", event)


def run_scan(path: str) -> dict:
    result = scan_directory(path)
    log_scan(result)
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("[OMNI] Usage: python -m src.ingest.scanner <path>")
        raise SystemExit(1)

    target = sys.argv[1]
    print(f"[OMNI] Scanning: {target}")
    result = run_scan(target)
    print(f"[OMNI] Scan complete. {result['file_count']} files found.")
