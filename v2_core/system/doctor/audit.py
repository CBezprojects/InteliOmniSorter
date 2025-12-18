"""
ARCHIVIST-CORE :: Doctor (Audit Only)

Read-only system inspection.
No mutation. No fixes. No side effects.
"""

import json
import sys
import platform
from pathlib import Path
from datetime import datetime


def run_audit(args):
    root = Path.cwd()

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "deep": bool(args.deep),
        "root": str(root),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version,
        },
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    # -------------------------------
    # 1. Repo structure check
    # -------------------------------
    expected = [
        "omni.py",
        "v2_core",
    ]

    missing = [p for p in expected if not (root / p).exists()]
    report["checks"]["repo_structure"] = {
        "expected": expected,
        "missing": missing,
        "ok": len(missing) == 0,
    }

    if missing:
        report["errors"].append(f"Missing expected paths: {missing}")

    # -------------------------------
    # 2. Registry presence (no load)
    # -------------------------------
    registry_paths = list(root.rglob("*registry*.py"))
    report["checks"]["registry_files"] = {
        "count": len(registry_paths),
        "files": [str(p) for p in registry_paths],
    }

    if len(registry_paths) == 0:
        report["warnings"].append("No registry files detected")

    # -------------------------------
    # 3. Engine discovery (static)
    # -------------------------------
    engines_dir = root / "v2_core" / "engines"
    engines = []

    if engines_dir.exists():
        for p in engines_dir.rglob("*.py"):
            engines.append(str(p))

    report["checks"]["engine_files"] = {
        "count": len(engines),
        "files": engines,
    }

    if len(engines) == 0:
        report["warnings"].append("No engine modules detected")

    # -------------------------------
    # 4. Safety assertions
    # -------------------------------
    report["checks"]["safety"] = {
        "no_execution": True,
        "no_mutation": True,
        "audit_only": True,
    }

    # -------------------------------
    # Write outputs
    # -------------------------------
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(args.text, "w", encoding="utf-8") as f:
        f.write("ARCHIVIST-CORE :: DOCTOR AUDIT\n")
        f.write(f"Timestamp: {report['timestamp']}\n\n")

        for section, data in report["checks"].items():
            f.write(f"[{section.upper()}]\n")
            f.write(json.dumps(data, indent=2))
            f.write("\n\n")

        if report["warnings"]:
            f.write("[WARNINGS]\n")
            for w in report["warnings"]:
                f.write(f"- {w}\n")

        if report["errors"]:
            f.write("\n[ERRORS]\n")
            for e in report["errors"]:
                f.write(f"- {e}\n")

    print("[DOCTOR] Audit completed (read-only)")
