# InteliOmniSorter V2 - Doctor (self-check system)

import os

REQUIRED_FOLDERS = [
    "v2_core",
    "v2_core/logs",
    "v2_core/temp",
    "v2_core/system",
    "v2_core/engines",
    "v2_core/gui"
]

def run_basic_checks():
    print("Doctor: running basic checks...")
    missing = []
    for folder in REQUIRED_FOLDERS:
        if not os.path.exists(folder):
            missing.append(folder)
    if missing:
        print("Doctor: missing folders:")
        for m in missing:
            print(" -", m)
    else:
        print("Doctor: all required folders exist.")
