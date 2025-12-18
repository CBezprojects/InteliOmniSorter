"""
InteliOmniSorter — Engine Registry (Lazy, Normalised)
"""

_ENGINE_REGISTRY = {
    "engines": {},
    "plugins": {},
    "system": {}
}

# Legacy compatibility map
_KIND_ALIASES = {
    "engine": "engines",
    "plugin": "plugins",
    "sys": "system"
}

def _normalise_kind(kind: str) -> str:
    if kind in _ENGINE_REGISTRY:
        return kind
    if kind in _KIND_ALIASES:
        return _KIND_ALIASES[kind]
    raise ValueError(f"Unknown registry kind: {kind}")

def register(kind: str, name: str, module):
    kind = _normalise_kind(kind)
    _ENGINE_REGISTRY[kind][name] = module

def get_registry():
    return _ENGINE_REGISTRY

def clear_registry():
    for k in _ENGINE_REGISTRY:
        _ENGINE_REGISTRY[k].clear()
