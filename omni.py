#!/usr/bin/env python3
"""
InteliOmniSorter :: CLI Entry Point
ARCHIVIST-CORE canonical spine
"""

import argparse
import sys



from pathlib import Path

# --------------------------------------------------
# ARCHIVIST-CORE bootstrap
# Ensure v2_core is on sys.path
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent
V2_CORE = ROOT / "v2_core"

if str(V2_CORE) not in sys.path:
    sys.path.insert(0, str(V2_CORE))
def main():
    parser = argparse.ArgumentParser(
        description="InteliOmniSorter CLI Tool"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # --------------------------------------------------
    # sort
    # --------------------------------------------------
    sort_parser = subparsers.add_parser(
        "sort",
        help="Run sorting operation"
    )

    # --------------------------------------------------
    # rollback
    # --------------------------------------------------
    rollback_parser = subparsers.add_parser(
        "rollback",
        help="Rollback last operation"
    )

    # --------------------------------------------------
    # doctor (audit-only)
    # --------------------------------------------------
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run read-only system audit (no mutation)"
    )

    doctor_parser.add_argument(
        "--mode",
        choices=["audit"],
        required=True,
        help="Doctor mode (audit only)"
    )

    doctor_parser.add_argument(
        "--deep",
        action="store_true",
        help="Enable deep inspection (still read-only)"
    )

    doctor_parser.add_argument(
        "--out",
        required=True,
        help="Path to JSON output report"
    )

    doctor_parser.add_argument(
        "--text",
        required=True,
        help="Path to human-readable text report"
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # Dispatch
    # --------------------------------------------------
    if args.command == "sort":
        print("[INFO] sort command invoked (stub)")
        sys.exit(0)

    elif args.command == "rollback":
        print("[INFO] rollback command invoked (stub)")
        sys.exit(0)

    elif args.command == "doctor":
        from system.doctor.audit import run_audit
        run_audit(args)
        sys.exit(0)

    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()

