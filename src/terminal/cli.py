from __future__ import annotations

import argparse
import json

from src.actions.dry_run_executor import run_dry_run
from src.actions.executor import apply_batch, confirm_apply
from src.actions.ledger import get_latest_batch, load_ledger
from src.classify.classifier import classify_path
from src.ingest.scanner import run_scan
from src.rules.rules_engine import run_plan
from src.safety.doctor import run_doctor
from src.safety.validator import run_validation
from src.terminal.report import save_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omni", description="OMNI terminal interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory safely")
    scan_parser.add_argument("path", help="Target directory path")
    scan_parser.add_argument("--json", action="store_true", help="Print JSON output")

    classify_parser = subparsers.add_parser("classify", help="Classify a single file path")
    classify_parser.add_argument("path", help="Target file path")
    classify_parser.add_argument("--json", action="store_true", help="Print JSON output")

    subparsers.add_parser("report", help="Generate OMNI report")

    plan_parser = subparsers.add_parser("plan", help="Generate dry-run file organization plan")
    plan_parser.add_argument("path", help="Target directory path")
    plan_parser.add_argument("--json", action="store_true", help="Print JSON output")

    dry_run_parser = subparsers.add_parser(
        "apply-dry-run", help="Simulate applying the validated plan"
    )
    dry_run_parser.add_argument("path", help="Target directory path")

    apply_parser = subparsers.add_parser("apply", help="Apply the most recent dry-run batch")
    apply_parser.add_argument("--batch-id", help="Specific dry-run batch id to apply")
    apply_parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")

    subparsers.add_parser("last-batch", help="Show the most recent dry-run batch")

    doctor_parser = subparsers.add_parser("doctor", help="Run OMNI health checks")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output")

    return parser


def _load_batch_by_id(batch_id: str) -> dict | None:
    for entry in load_ledger():
        if entry["batch_id"] == batch_id:
            return entry
    return None


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


def _print_plan_preview(validated: dict) -> None:
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

    print("[OMNI] Sample planned destinations:")
    for item in validated["plan"][:10]:
        status = item["status"].upper()
        reason = f" ({item['reason']})" if item["reason"] else ""
        print(f"[OMNI] {status} :: {item['source']} -> {item['destination']}{reason}")

    if validated["total_files"] > 10:
        print(f"[OMNI] ... ({validated['total_files'] - 10} more)")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        result = run_scan(args.path)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("[OMNI] Scan complete.")
            print(f"[OMNI] Path: {result['scan_path']}")
            print(f"[OMNI] Files discovered: {result['file_count']}")
            print("[OMNI] Category summary:")
            for category, count in result["category_summary"].items():
                print(f"[OMNI] - {category}: {count}")
        return 0

    if args.command == "classify":
        result = classify_path(args.path)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[OMNI] Suffix: {result['suffix'] or '(none)'}")
            print(f"[OMNI] Category: {result['category']}")
        return 0

    if args.command == "plan":
        scan_result = run_scan(args.path)
        plan = run_plan(scan_result)
        validated = run_validation(plan)

        if args.json:
            print(json.dumps(validated, indent=2, ensure_ascii=False))
        else:
            _print_plan_preview(validated)
        return 0

    if args.command == "apply-dry-run":
        scan_result = run_scan(args.path)
        plan = run_plan(scan_result)
        validated = run_validation(plan)
        action_result = run_dry_run(validated)

        print("[OMNI] Dry-run execution preview:")
        print(f"[OMNI] Batch ID: {action_result['batch_id']}")
        print(f"[OMNI] Files: {action_result['total_files']}")
        print(f"[OMNI] Planned directories: {len(action_result['directory_plan'])}")
        print(f"[OMNI] Safe moves: {action_result['safety_summary']['safe']}")
        print(f"[OMNI] Conflicts: {action_result['safety_summary']['conflicts']}")
        print(f"[OMNI] Blocked moves: {action_result['safety_summary']['blocked']}")

        _print_git_summary(action_result["git_protection"])

        print("[OMNI] Sample actions:")
        shown = 0
        for item in action_result["actions"]:
            if shown >= 10:
                break
            if item["will_move"]:
                print(f"[OMNI] MOVE (dry-run) :: {item['source']} -> {item['destination']}")
            else:
                print(
                    "[OMNI] BLOCKED :: "
                    f"{item['source']} -> {item['destination']} "
                    f"({item['reason']})"
                )
            shown += 1

        if action_result["total_files"] > 10:
            print(f"[OMNI] ... ({action_result['total_files'] - 10} more)")

        return 0

    if args.command == "apply":
        batch = _load_batch_by_id(args.batch_id) if args.batch_id else get_latest_batch()

        if batch is None:
            print("[OMNI] No dry-run batch available to apply.")
            return 0

        if batch.get("mode") != "dry-run":
            print("[OMNI] Latest batch is not a dry-run batch.")
            return 0

        if not args.yes:
            approved = confirm_apply(batch["batch_id"], batch["total_files"])
            if not approved:
                print("[OMNI] Apply cancelled.")
                return 0

        result = apply_batch(batch["batch_id"])
        summary = result["execution_summary"]

        print("[OMNI] Apply complete.")
        print(f"[OMNI] Batch ID: {result['batch_id']}")
        print(f"[OMNI] Applied: {summary['applied']}")
        print(f"[OMNI] Blocked: {summary['blocked']}")
        print(f"[OMNI] Failed: {summary['failed']}")
        return 0

    if args.command == "last-batch":
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

    if args.command == "report":
        save_report()
        return 0

    if args.command == "doctor":
        result = run_doctor()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
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

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
