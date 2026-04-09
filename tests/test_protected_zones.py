from src.safety.protected_zones import is_in_protected_zone


def test_protected_zone_detection():
    registry = {"protected_zones": [".git", ".venv"], "protected_patterns": ["*.log"]}

    protected, reason = is_in_protected_zone("/project/.git/config", registry)
    assert protected
    assert ".git" in reason

    protected, reason = is_in_protected_zone("/project/file.log", registry)
    assert protected
    assert "*.log" in reason

    protected, _ = is_in_protected_zone("/project/file.py", registry)
    assert not protected
