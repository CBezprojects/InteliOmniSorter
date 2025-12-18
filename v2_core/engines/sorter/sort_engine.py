"""
InteliOmniSorter - Sort Engine (Phase 6 Integration)

- Loads RuleEngine automatically via Automount V2
- Expands rule templates like {year}/{month}/{ext}
- Uses rule-based destinations
- Falls back to timeline sorting
"""

REGISTER = {
    "name": "sort_engine",
    "type": "engine"
}

import os
from pathlib import Path
from datetime import datetime


def _get_registry():
    """
    Lazy registry fetch (no import-time bootstrap).
    omni.py should call discover() once at startup.
    """
    try:
        from v2_core.system.registry import get_registry
        return get_registry()
    except Exception:
        return {"engines": {}, "plugins": {}, "system": {}}


class SortEngine:
    engine_name = "sort_engine"


    def _load_rule_engine(self):
        reg = _get_registry()
        rule_mod = (
            reg["engines"].get("rule_engine") or
            reg["plugins"].get("rule_engine") or
            reg["system"].get("rule_engine")
        )
        if not rule_mod:
            return None
        RuleEngine = getattr(rule_mod, "RuleEngine", None)
        return RuleEngine() if RuleEngine else None

    def __init__(self, simulated=True):
        self.simulated = simulated
        self.logs = []
        self.rollback_stack = []
        self.faces_engine = _get_registry()["engines"].get("faces_engine")
        self.rule_engine = self._load_rule_engine()

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------
    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.logs.append(entry)
        print(entry)

    def snapshot(self, file_path):
        self.rollback_stack.append({
            "file": str(file_path),
            "exists": Path(file_path).exists()
        })

    # --------------------------------------------------------
    # Safe move
    # --------------------------------------------------------
    def safe_move(self, src, dst):
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
            self.log(f"[ERROR] Failed move: {e}")
            return False

    # --------------------------------------------------------
    # Extract tags + metadata
    # --------------------------------------------------------
    def classify(self, file_path):
        tags = {}
        ext = Path(file_path).suffix.lower()

        tags["ext"] = ext

        # Image/video detection
        if ext in [".jpg", ".jpeg", ".png"]:
            tags["type"] = "image"
        elif ext in [".mp4", ".mov", ".avi"]:
            tags["type"] = "video"
        else:
            tags["type"] = "other"

        # Timestamp
        ts = datetime.fromtimestamp(Path(file_path).stat().st_mtime)
        tags["year"] = ts.year
        tags["month"] = ts.strftime("%m")
        tags["day"] = ts.strftime("%d")

        # Faces (optional)
        if self.faces_engine:
            try:
                mod = self.faces_engine
                if hasattr(mod, "detect_faces"):
                    tags["faces"] = mod.detect_faces(file_path)
            except Exception as e:
                self.log(f"[WARN] Face engine failed: {e}")

        return tags

    # --------------------------------------------------------
    # Apply rules + expand templates
    # --------------------------------------------------------
    def expand_target(self, template, tags):
        for key, value in tags.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template

    def resolve_destination(self, tags, file_name):
        # 1) Try RuleEngine
        if self.rule_engine:
            target = self.rule_engine.evaluate(tags)
            if target:
                return Path(self.expand_target(target, tags)) / file_name

        # 2) Fallback – timeline sort
        fallback = f"sorted/other/{tags['year']}/{tags['month']}/"
        return Path(fallback) / file_name

    # --------------------------------------------------------
    # Main entry
    # --------------------------------------------------------
    def run(self, input_folder):
        self.log(f"SortEngine Phase 6 started (simulated={self.simulated})")

        input_folder = Path(input_folder)
        if not input_folder.exists():
            self.log("[ERROR] Input folder missing.")
            return

        for file in input_folder.rglob("*.*"):
            if file.is_dir():
                continue

            tags = self.classify(file)
            dst = self.resolve_destination(tags, file.name)

            self.safe_move(str(file), str(dst))

        self.log("SortEngine Phase 6 completed.")
        return self.logs, self.rollback_stack


if __name__ == "__main__":
    engine = SortEngine(simulated=True)
    engine.run("sample_input")


