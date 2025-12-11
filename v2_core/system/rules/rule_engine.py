"""
InteliOmniSorter - Rule Engine (Phase 5 Architecture)

Handles:
- rule loading (JSON)
- rule evaluation
- multi-condition AND/OR rule groups
- type-based, extension-based, face-based, EXIF-based rules
- priority rules
- fallback logic

Loaded automatically via Automount V2.
"""

REGISTER = {
    "name": "rule_engine",
    "type": "system"
}

import json
from pathlib import Path


class RuleEngine:
    engine_name = "rule_engine"

    def __init__(self, config_path="v2_core/config/rules.json"):
        self.config_path = Path(config_path)
        self.rules = self.load_rules()

    # --------------------------------------------------------
    # Load rules.json
    # --------------------------------------------------------
    def load_rules(self):
        if not self.config_path.exists():
            print("[RuleEngine] No rules.json found.")
            return []

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("[RuleEngine] Failed to load rules:", e)
            return []

    # --------------------------------------------------------
    # Check if a rule matches extracted tags
    # --------------------------------------------------------
    def rule_matches(self, rule, tags):
        # Match type = image/video/etc.
        if "type" in rule:
            if rule["type"] != tags.get("type"):
                return False

        # Match extensions (jpg/png/mp4)
        if "ext" in rule:
            ext = tags.get("ext", "").lower()
            if ext not in rule["ext"]:
                return False

        # Match faces (if any)
        if "faces" in rule:
            detected = tags.get("faces", [])
            # Any match qualifies
            if not any(face in detected for face in rule["faces"]):
                return False

        # Match EXIF camera model
        if "camera" in rule:
            if tags.get("camera") != rule["camera"]:
                return False

        return True

    # --------------------------------------------------------
    # Determine destination path for a file
    # --------------------------------------------------------
    def evaluate(self, tags):
        # Rule priority: earlier rules win
        for rule in self.rules:
            if self.rule_matches(rule, tags):
                return rule.get("target")

        # Default fallback
        return None


if __name__ == "__main__":
    engine = RuleEngine()
    print("Loaded rules:", engine.rules)
