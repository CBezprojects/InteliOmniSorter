# ONLY PATCHED PART SHOWN — KEEP YOUR FILE AND ADD THIS FUNCTION


def _print_protected_zone_summary(registry: dict) -> None:
    print("[OMNI] Protected zones active:")
    for zone in registry.get("protected_zones", []):
        print(f"[OMNI] - zone: {zone}")
    for pattern in registry.get("protected_patterns", []):
        print(f"[OMNI] - pattern: {pattern}")
