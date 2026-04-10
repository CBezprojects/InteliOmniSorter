from pathlib import Path


def check_file_exists(path: Path) -> bool:
    """Check if a file exists."""
    return path.exists()


def check_destination_safe(dest: Path) -> bool:
    """Ensure destination does not already exist."""
    return not dest.exists()


def validate_move(source: Path, destination: Path) -> dict:
    """
    Validate a file move operation.

    Returns:
        dict with status and reason
    """
    if not source.exists():
        return {"ok": False, "reason": "Source file does not exist"}

    if destination.exists():
        return {"ok": False, "reason": "Destination already exists"}

    return {"ok": True, "reason": "Safe to move"}

from .checks import validate_move

