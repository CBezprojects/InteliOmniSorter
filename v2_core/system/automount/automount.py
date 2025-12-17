"""
InteliOmniSorter - Automount V3 (Fixed Root)
"""

import importlib.util
from pathlib import Path

# Correct root: CleanRoot/
ROOT = Path(__file__).resolve().parents[3]

def load_module(path):
    print(f"[AutoMount] Loading: {path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def mount_all():
    base = ROOT / "v2_core"

    registry = {
        "engines": {},
        "plugins": {},
        "system": {}
    }

    print(f"[AutoMount] Root = {ROOT}")
    print(f"[AutoMount] Base = {base}")

    # ---- LOAD ENGINES ----
    engines_dir = base / "engines"
    print(f"[AutoMount] Scanning engines: {engines_dir}")

    if engines_dir.exists():
        for file in engines_dir.rglob("*.py"):
            if file.name in ["__init__.py", "automount.py"]:
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                name = mod.REGISTER["name"]
                print(f"[AutoMount] Engine registered: {name}")
                registry["engines"][name] = mod
    else:
        print(f"[ERROR] Engines path does NOT exist: {engines_dir}")

    # ---- LOAD PLUGINS ----
    plugins_dir = base / "plugins"
    if plugins_dir.exists():
        for file in plugins_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                registry["plugins"][mod.REGISTER['name']] = mod

    # ---- LOAD SYSTEM MODULES ----
    system_dir = base / "system"
    if system_dir.exists():
        for file in system_dir.rglob("*.py"):
            if file.name in ["__init__.py", "automount.py"]:
                continue
            mod = load_module(file)
            if hasattr(mod, "REGISTER"):
                registry["system"][mod.REGISTER['name']] = mod

    print("[AutoMount] DONE.")
    return registry
