from __future__ import annotations

import json
from pathlib import Path

REQUIRED_DIRS = [
    "src",
    "src/ingest",
    "src/logger",
    "src/terminal",
    "src/safety",
    "config",
    "docs",
    "logs",
    "tests",
]


def check_required_dirs() -> list[dict]:
    results = []
    for directory in REQUIRED_DIRS:
        path = Path(directory)
        results.append(
            {
                "check": "required_dir",
                "target": directory,
                "ok": path.exists() and path.is_dir(),
            }
        )
    return results


def check_registry() -> dict:
    registry_path = Path("config/registry.json")
    if not registry_path.exists():
        return {"check": "registry", "target": str(registry_path), "ok": False, "reason": "missing"}

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        ok = isinstance(data, dict)
        return {"check": "registry", "target": str(registry_path), "ok": ok}
    except Exception as exc:
        return {
            "check": "registry",
            "target": str(registry_path),
            "ok": False,
            "reason": str(exc),
        }


def run_doctor() -> dict:
    checks = []
    checks.extend(check_required_dirs())
    checks.append(check_registry())

    passed = sum(1 for c in checks if c["ok"])
    failed = sum(1 for c in checks if not c["ok"])

    return {
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": len(checks),
        },
        "checks": checks,
    }


if __name__ == "__main__":
    report = run_doctor()
    print("[OMNI] Doctor report")
    for check in report["checks"]:
        status = "OK" if check["ok"] else "FAIL"
        print(f"[OMNI] {status} :: {check['check']} :: {check['target']}")
    print(
        f"[OMNI] Summary: {report['summary']['passed']} passed, "
        f"{report['summary']['failed']} failed"
    )
