"""
InteliOmniSorter - Rollback Engine (Phase 7)

Handles:
- restoring moved files back to their original location
- JSON rollback snapshots
- safety checks
- conflict detection
- dry-run preview
"""

REGISTER = {
    "name": "rollback_engine",
    "type": "system"
}

import os
import json
from pathlib import Path
from datetime import datetime


class RollbackEngine:
    engine_name = "rollback_engine"

    def __init__(self, log_file="rollback_log.json"):
        self.log_file = Path(log_file)
        self.entries = []

    # --------------------------------------------------------
    # Load rollback entries
    # --------------------------------------------------------
    def load(self):
        if not self.log_file.exists():
            print("[Rollback] No rollback log found.")
            return []

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        except:
            print("[Rollback] Failed to load rollback log.")
            self.entries = []

        return self.entries

    # --------------------------------------------------------
    # Save rollback entries
    # --------------------------------------------------------
    def save(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=4)

    # --------------------------------------------------------
    # Add a rollback entry
    # --------------------------------------------------------
    def record(self, src_before, dst_after):
        entry = {
            "before": str(src_before),
            "after": str(dst_after),
            "timestamp": datetime.now().isoformat()
        }
        self.entries.append(entry)
        self.save()

    # --------------------------------------------------------
    # Perform rollback
    # --------------------------------------------------------
    def rollback(self, dry_run=True):
        self.load()

        if not self.entries:
            print("[Rollback] Nothing to rollback.")
            return

        print(f"[Rollback] Processing {len(self.entries)} items...")

        for item in reversed(self.entries):
            src_before = Path(item["before"])
            dst_after = Path(item["after"])

            # If original location exists, skip
            if dst_after.exists() and src_before.exists():
                print(f"[SKIP] {dst_after} already exists.")
                continue

            if dry_run:
                print(f"[PREVIEW] Would restore: {dst_after} -> {src_before}")
                continue

            # Ensure folder exists
            os.makedirs(src_before.parent, exist_ok=True)

            try:
                os.rename(dst_after, src_before)
                print(f"[RESTORE] {dst_after} -> {src_before}")
            except Exception as e:
                print(f"[ERROR] Failed rollback: {e}")

        print("[Rollback] Completed.")
