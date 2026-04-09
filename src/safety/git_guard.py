from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git_status(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git status failed")
    return result.stdout


def detect_git_repo(start_path: str | Path) -> dict:
    path = Path(start_path).resolve()
    search_root = path if path.is_dir() else path.parent

    for candidate in [search_root, *search_root.parents]:
        if (candidate / ".git").exists():
            return {
                "active": True,
                "repo_root": str(candidate),
            }

    return {
        "active": False,
        "repo_root": None,
    }


def parse_git_status_output(output: str) -> dict[str, dict]:
    protected: dict[str, dict] = {}

    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue

        status = raw_line[:2]
        rel_path = raw_line[3:].strip()

        if not rel_path:
            continue

        reason = classify_git_status(status)
        protected[rel_path] = {
            "git_status": status,
            "reason": reason,
        }

    return protected


def classify_git_status(status: str) -> str:
    if status == "??":
        return "git untracked file"
    if status[0] != " ":
        return "git staged change"
    if status[1] != " ":
        return "git modified file"
    return "git protected file"


def build_git_protection_map(scan_path: str | Path) -> dict:
    repo_info = detect_git_repo(scan_path)
    if not repo_info["active"]:
        return {
            "active": False,
            "repo_root": None,
            "protected": {},
            "summary": {
                "protected_total": 0,
                "untracked": 0,
                "modified": 0,
                "staged": 0,
            },
        }

    repo_root = Path(repo_info["repo_root"])
    output = _run_git_status(repo_root)
    protected = parse_git_status_output(output)

    untracked = 0
    modified = 0
    staged = 0

    for item in protected.values():
        reason = item["reason"]
        if reason == "git untracked file":
            untracked += 1
        elif reason == "git modified file":
            modified += 1
        elif reason == "git staged change":
            staged += 1

    return {
        "active": True,
        "repo_root": str(repo_root),
        "protected": protected,
        "summary": {
            "protected_total": len(protected),
            "untracked": untracked,
            "modified": modified,
            "staged": staged,
        },
    }


def get_git_protection_for_path(
    source_path: str | Path,
    protection_map: dict,
) -> dict | None:
    if not protection_map.get("active"):
        return None

    repo_root = Path(protection_map["repo_root"])
    source = Path(source_path).resolve()

    try:
        rel_path = source.relative_to(repo_root).as_posix()
    except ValueError:
        return None

    protected = protection_map.get("protected", {})
    return protected.get(rel_path)
