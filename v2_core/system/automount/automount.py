"""
InteliOmniSorter — Automount (Discovery Only)

- Scans v2_core/{engines,plugins,system} for .py
- Loads modules dynamically
- Registers modules that expose REGISTER = {"name": "...", "type": "..."}
- No recursion safeguards required because engines MUST NOT call discover() at import time.

Bootstrap rule:
- omni.py calls discover() once, then uses registry.get_registry()
"""

from pathlib import Path
import importlib.util

from v2_core.system.registry import register

ROOT = Path(__file__).resolve().parents[2]  # ...\v2_core

def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def discover(verbose: bool = False):
    base = ROOT  # points at ...\v2_core

    for kind in ["engines", "plugins", "system"]:
        scan_dir = base / kind
        if not scan_dir.exists():
            continue

        for file in scan_dir.rglob("*.py"):
            if file.name in ["__init__.py", "automount.py"]:
                continue
            if file.name.startswith("_"):
                continue

            if verbose:
                print(f"[AutoMount] Loading: {file}")

            mod = _load_module(file)

            if hasattr(mod, "REGISTER"):
                meta = getattr(mod, "REGISTER")
                name = meta.get("name")
                mtype = meta.get("type", kind)

                if name:
                    register(mtype, name, mod)
                    if verbose:
                        print(f"[AutoMount] Registered: {mtype}:{name}")
