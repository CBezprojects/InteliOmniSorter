from __future__ import annotations

import argparse
import json

from src.classify.classifier import classify_path
from src.ingest.scanner import run_scan
from src.safety.doctor import run_doctor
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

    doctor_parser = subparsers.add_parser("doctor", help="Run OMNI health checks")
    doctor_parser.add_argument("--json", action="store_true", help="Print JSON output")

    return parser


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
