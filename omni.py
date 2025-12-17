"""
InteliOmniSorter - CLI Launcher (Phase 9)

Provides:
- sort command
- rollback preview
- rollback apply
- automatic loading of engines via Automount V2
"""

import argparse
import sys
from pathlib import Path

# -------------------------------------------------------
# Ensure ROOT is in PYTHONPATH
# -------------------------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -------------------------------------------------------
# AutoMount V2
# -------------------------------------------------------
import importlib.util

# -------------------------------------------------------
# Universal Automount Loader (works everywhere)
# -------------------------------------------------------
AUTO_PATH = ROOT / "v2_core" / "system" / "automount" / "automount.py"

spec = importlib.util.spec_from_file_location("automount", AUTO_PATH)
automount = importlib.util.module_from_spec(spec)
spec.loader.exec_module(automount)

mount_all = automount.mount_all

REGISTRY = mount_all()

# Engines
SortEngine = None
RollbackEngine = None

# Detect engines
if "sort_engine" in REGISTRY["engines"]:
    SortEngine = REGISTRY["engines"]["sort_engine"].SortEngine

if "rollback_engine" in REGISTRY["system"]:
    RollbackEngine = REGISTRY["system"]["rollback_engine"].RollbackEngine

# -------------------------------------------------------
# CLI
# -------------------------------------------------------
def cli():
    parser = argparse.ArgumentParser(description="InteliOmniSorter CLI Tool")
    sub = parser.add_subparsers(dest="command")

    # SORT
    sort_cmd = sub.add_parser("sort")
    sort_cmd.add_argument("--input", required=True, help="Folder to sort")
    sort_cmd.add_argument("--simulate", action="store_true", help="Simulated run")

    # ROLLBACK
    rb_cmd = sub.add_parser("rollback")
    rb_cmd.add_argument("--preview", action="store_true")
    rb_cmd.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    # -------------------------
    # SORT
    # -------------------------
    if args.command == "sort":
        if not SortEngine:
            print("[ERROR] SortEngine not found in REGISTRY.")
            return

        eng = SortEngine(simulated=args.simulate)
        eng.run(args.input)
        return

    # -------------------------
    # ROLLBACK
    # -------------------------
    if args.command == "rollback":
        if not RollbackEngine:
            print("[ERROR] RollbackEngine not loaded.")
            return

        rb = RollbackEngine()

        if args.preview:
            rb.rollback(dry_run=True)
            return

        if args.apply:
            rb.rollback(dry_run=False)
            return

        print("[ERROR] Use --preview or --apply for rollback.")
        return

    parser.print_help()


if __name__ == "__main__":
    cli()


