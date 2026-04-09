from __future__ import annotations

import argparse
import json
import shlex

from src.actions.dry_run_executor import run_dry_run
from src.actions.ledger import get_latest_batch
from src.classify.classifier import classify_path
from src.ingest.scanner import run_scan
from src.rules.rules_engine import run_plan
from src.safety.doctor import run_doctor
from src.safety.validator import run_validation

BANNER = """
[OMNI] InteliOmniSorter Terminal
[OMNI] Type 'help' for commands.
""".strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omni", description="OMNI terminal interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory safely")
    scan_parser.add_argument("path", help="Target directory path")
    scan_parser.add_argument("--json", action="store_true", help="Print JSON output")

    classify_parser = subparsers.add_parser("classify", help="Classify a single file path")
    classify_parser.add_argument("path", help="Target file path")
    classify_parser.add_argument("--json", action="store_true", help="Print JSON output")

    plan_parser = subparsers.add_parser("plan", help="Generate dry-run file organization plan")
    plan_parser.add_argument("path", help="Target directory path")
    plan_parser.add_argument("--json", action="store_true", help="Print JSON output")

    dry_parser = subparsers.add_parser(
        "apply-dry-run",
        help="Simulate applying the validated plan",
    )
    dry_parser.add_argument("path", help="Target directory path")
    dry_parser.add_argument("--json", action="store_true", help="Print JSON output")

    doctor_parser = subparsers.add_parser("doctor", help="Run OMNI health checks")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output")

    subparsers.add_parser("last-batch", help="Show the most recent dry-run batch")
    subparsers.add_parser("shell", help="Start interactive OMNI shell")

    return parser


def _print_git_summary(git_protection: dict) -> None:
    if not git_protection.get("active"):
        print("[OMNI] Git protection active: no")
        return

    summary = git_protection["summary"]
    print("[OMNI] Git protection active.")
    print(
        "[OMNI] Protected files: "
        f"{summary['protected_total']} "
        f"(untracked={summary['untracked']}, "
        f"modified={summary['modified']}, "
        f"staged={summary['staged']})"
    )


def cmd_scan(path: str, json_mode: bool = False) -> int:
    result = run_scan(path)
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("[OMNI] Scan complete.")
    print(f"[OMNI] Path: {result['scan_path']}")
    print(f"[OMNI] Files discovered: {result['file_count']}")
    print("[OMNI] Category summary:")
    for category, count in result["category_summary"].items():
        print(f"[OMNI] - {category}: {count}")
    return 0


def cmd_classify(path: str, json_mode: bool = False) -> int:
    result = classify_path(path)
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"[OMNI] Path: {path}")
    print(f"[OMNI] Suffix: {result['suffix'] or '(none)'}")
    print(f"[OMNI] Category: {result['category']}")
    if "subtype" in result:
        print(f"[OMNI] Subtype: {result['subtype']}")
    return 0


def cmd_plan(path: str, json_mode: bool = False) -> int:
    scan_result = run_scan(path)
    plan = run_plan(scan_result)
    validated = run_validation(plan)

    if json_mode:
        print(json.dumps(validated, indent=2, ensure_ascii=False))
        return 0

    print("[OMNI] Dry-run plan generated:")
    print(f"[OMNI] Files: {validated['total_files']}")
    print("[OMNI] Plan summary by category:")
    for category, count in validated["summary"]["by_category"].items():
        print(f"[OMNI] - {category}: {count}")

    print("[OMNI] Safety summary:")
    print(f"[OMNI] - safe: {validated['safety_summary']['safe']}")
    print(f"[OMNI] - conflicts: {validated['safety_summary']['conflicts']}")
    print(f"[OMNI] - blocked: {validated['safety_summary']['blocked']}")

    _print_git_summary(validated["git_protection"])

    if "protected_zones" in validated:
        zones = validated["protected_zones"]
        if zones.get("protected_zones") or zones.get("protected_patterns"):
            print("[OMNI] Protected zones active:")
            for zone in zones.get("protected_zones", []):
                print(f"[OMNI] - zone: {zone}")
            for pattern in zones.get("protected_patterns", []):
                print(f"[OMNI] - pattern: {pattern}")

    print("[OMNI] Sample planned destinations:")
    for item in validated["plan"][:10]:
        status = item["status"].upper()
        reason = f" ({item['reason']})" if item.get("reason") else ""
        print(f"[OMNI] {status} :: {item['source']} -> {item['destination']}{reason}")

    if validated["total_files"] > 10:
        print(f"[OMNI] ... ({validated['total_files'] - 10} more)")
    return 0


def cmd_apply_dry_run(path: str, json_mode: bool = False) -> int:
    scan_result = run_scan(path)
    plan = run_plan(scan_result)
    validated = run_validation(plan)
    result = run_dry_run(validated)

    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("[OMNI] Dry-run execution preview:")
    print(f"[OMNI] Batch ID: {result['batch_id']}")
    print(f"[OMNI] Files: {result['total_files']}")
    print(f"[OMNI] Planned directories: {len(result['directory_plan'])}")
    print(f"[OMNI] Safe moves: {result['safety_summary']['safe']}")
    print(f"[OMNI] Conflicts: {result['safety_summary']['conflicts']}")
    print(f"[OMNI] Blocked moves: {result['safety_summary']['blocked']}")

    _print_git_summary(result["git_protection"])

    print("[OMNI] Sample actions:")
    for item in result["actions"][:10]:
        if item["will_move"]:
            print(f"[OMNI] MOVE (dry-run) :: {item['source']} -> {item['destination']}")
        else:
            print(
                "[OMNI] BLOCKED :: "
                f"{item['source']} -> {item['destination']} "
                f"({item['reason']})"
            )

    if result["total_files"] > 10:
        print(f"[OMNI] ... ({result['total_files'] - 10} more)")
    return 0


def cmd_doctor(json_mode: bool = False) -> int:
    result = run_doctor()
    if json_mode:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("[OMNI] Doctor complete.")
    print(
        f"[OMNI] Passed: {result['summary']['passed']} | "
        f"Failed: {result['summary']['failed']} | "
        f"Total: {result['summary']['total']}"
    )
    for check in result["checks"]:
        status = "OK" if check["ok"] else "FAIL"
        print(f"[OMNI] {status} :: {check['check']} :: {check['target']}")
    return 0


def cmd_last_batch() -> int:
    batch = get_latest_batch()
    if batch is None:
        print("[OMNI] No dry-run batches recorded yet.")
        return 0

    print("[OMNI] Latest dry-run batch:")
    print(f"[OMNI] Batch ID: {batch['batch_id']}")
    print(f"[OMNI] Timestamp: {batch['timestamp']}")
    print(f"[OMNI] Scan path: {batch['scan_path']}")
    print(f"[OMNI] Files: {batch['total_files']}")
    print(f"[OMNI] Safe: {batch['safety_summary']['safe']}")
    print(f"[OMNI] Conflicts: {batch['safety_summary']['conflicts']}")
    print(f"[OMNI] Blocked: {batch['safety_summary']['blocked']}")
    print(f"[OMNI] Planned directories: {len(batch['directory_plan'])}")
    return 0


def run_shell() -> int:
    print(BANNER)
    while True:
        try:
            raw = input("[OMNI] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[OMNI] Terminal closed.")
            return 0

        if not raw:
            continue

        if raw in {"exit", "quit"}:
            print("[OMNI] Goodbye.")
            return 0

        if raw == "help":
            print("[OMNI] Commands:")
            print("[OMNI]   help")
            print("[OMNI]   scan <path>")
            print("[OMNI]   classify <path>")
            print("[OMNI]   plan <path>")
            print("[OMNI]   apply-dry-run <path>")
            print("[OMNI]   doctor")
            print("[OMNI]   last-batch")
            print("[OMNI]   exit")
            continue

        try:
            argv = shlex.split(raw)
            dispatch(argv)
        except SystemExit:
            print("[OMNI] Invalid command.")
        except Exception as exc:
            print(f"[OMNI] ERROR :: {exc}")


def dispatch(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return cmd_scan(args.path, getattr(args, "json", False))
    if args.command == "classify":
        return cmd_classify(args.path, getattr(args, "json", False))
    if args.command == "plan":
        return cmd_plan(args.path, getattr(args, "json", False))
    if args.command == "apply-dry-run":
        return cmd_apply_dry_run(args.path, getattr(args, "json", False))
    if args.command == "doctor":
        return cmd_doctor(getattr(args, "json", False))
    if args.command == "last-batch":
        return cmd_last_batch()
    if args.command == "shell":
        return run_shell()

    parser.print_help()
    return 1


def main() -> int:
    return dispatch(None)  # argparse reads sys.argv when None is passed


if __name__ == "__main__":
    raise SystemExit(main())
