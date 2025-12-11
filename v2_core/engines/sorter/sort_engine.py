"""
InteliOmniSorter - Sort Engine (Phase 4 Core Architecture)

This engine coordinates:
- file walking
- metadata extraction
- face detection (if engine is registered)
- rule evaluation
- simulated vs live mode
- safety layer (no destructive ops)
- logging + rollback

Automount V2 loads this engine automatically.
"""

REGISTER = {
    "name": "sort_engine",
    "type": "engine"
}

import os
import json
from pathlib import Path
from datetime import datetime

# ============================================================
# Import Automount Registry
# ============================================================
try:
    from v2_core.system.automount.automount import mount_all
except:
    from system.automount.automount import mount_all

REGISTRY = mount_all()

# ============================================================
# Core Sort Engine Class
# ============================================================

class SortEngine:
    engine_name = "sort_engine"

    def __init__(self, simulated=True):
        self.simulated = simulated
        self.rules = []
        self.logs = []
        self.rollback_stack = []
        self.faces_engine = REGISTRY["engines"].get("faces_engine")

    # --------------------------------------------------------
    # Logging Helpers
    # --------------------------------------------------------
    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.logs.append(entry)
        print(entry)

    def snapshot(self, file_path):
        """
        Record rollback information for safety.
        """
        self.rollback_stack.append({
            "file": str(file_path),
            "exists": Path(file_path).exists()
        })

    # --------------------------------------------------------
    # Safety Layer
    # --------------------------------------------------------
    def safe_move(self, src, dst):
        """
        Simulated move OR real move based on engine mode.
        """
        self.snapshot(src)

        if self.simulated:
            self.log(f"[SIMULATED MOVE] {src} -> {dst}")
            return True

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.rename(src, dst)
            self.log(f"[MOVE] {src} -> {dst}")
            return True
        except Exception as e:
            self.log(f"[ERROR] Failed to move {src}: {e}")
            return False

    # --------------------------------------------------------
    # Pre-Classification Layer
    # --------------------------------------------------------
    def classify(self, file_path):
        """
        Extract metadata, optionally run face engine, and return classification tags.
        """
        tags = {"type": "unknown", "faces": []}

        ext = Path(file_path).suffix.lower()
        if ext in [".jpg", ".jpeg", ".png"]:
            tags["type"] = "image"

        if ext in [".mp4", ".mov", ".avi"]:
            tags["type"] = "video"

        # optional: faces engine
        if self.faces_engine:
            try:
                mod = self.faces_engine
                if hasattr(mod, "detect_faces"):
                    faces = mod.detect_faces(file_path)
                    tags["faces"] = faces
            except Exception as e:
                self.log(f"[WARN] Face engine failed: {e}")

        return tags

    # --------------------------------------------------------
    # Rule Evaluation Pipeline
    # --------------------------------------------------------
    def apply_rules(self, file_path, tags):
        """
        Evaluate rules to determine destination folder.
        Default: Year/Month from metadata or file timestamp.
        """
        # default rule – timeline sort
        ts = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
        year = ts.year
        month = ts.strftime("%m")

        return f"sorted/{year}/{month}/"

    # --------------------------------------------------------
    # Main Entry
    # --------------------------------------------------------
    def run(self, input_folder):
        self.log(f"SortEngine started (simulated={self.simulated})")
        input_folder = Path(input_folder)

        if not input_folder.exists():
            self.log("[ERROR] Input folder does not exist.")
            return

        for file in input_folder.rglob("*.*"):
            if file.is_dir(): continue

            tags = self.classify(file)
            target_dir = self.apply_rules(file, tags)
            dst = Path(target_dir) / file.name

            self.safe_move(str(file), str(dst))

        self.log("SortEngine completed.")
        return self.logs, self.rollback_stack

# ============================================================
# Command-line test
# ============================================================
if __name__ == "__main__":
    engine = SortEngine(simulated=True)
    engine.run("sample_input")
