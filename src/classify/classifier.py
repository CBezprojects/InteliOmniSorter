from __future__ import annotations

from collections import Counter
from pathlib import Path

CATEGORY_MAP: dict[str, str] = {
    # images
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".gif": "image",
    ".bmp": "image",
    ".webp": "image",
    ".tif": "image",
    ".tiff": "image",
    ".svg": "image",
    # documents
    ".pdf": "document",
    ".doc": "document",
    ".docx": "document",
    ".txt": "document",
    ".rtf": "document",
    ".odt": "document",
    ".md": "document",
    ".csv": "document",
    ".xls": "document",
    ".xlsx": "document",
    ".ppt": "document",
    ".pptx": "document",
    # archives
    ".zip": "archive",
    ".rar": "archive",
    ".7z": "archive",
    ".tar": "archive",
    ".gz": "archive",
    ".bz2": "archive",
    ".xz": "archive",
    # audio
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".aac": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    # video
    ".mp4": "video",
    ".mkv": "video",
    ".avi": "video",
    ".mov": "video",
    ".wmv": "video",
    ".webm": "video",
    ".m4v": "video",
    # code
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".tsx": "code",
    ".jsx": "code",
    ".json": "code",
    ".yaml": "code",
    ".yml": "code",
    ".toml": "code",
    ".xml": "code",
    ".html": "code",
    ".css": "code",
    ".scss": "code",
    ".sh": "code",
    ".bat": "code",
    ".ps1": "code",
    ".java": "code",
    ".c": "code",
    ".cpp": "code",
    ".h": "code",
    ".hpp": "code",
    ".go": "code",
    ".rs": "code",
    ".php": "code",
    ".sql": "code",
}

NO_EXTENSION_CATEGORY = "unknown"
UNKNOWN_CATEGORY = "unknown"


def classify_suffix(suffix: str) -> str:
    normalized = suffix.lower().strip()
    if not normalized:
        return NO_EXTENSION_CATEGORY
    return CATEGORY_MAP.get(normalized, UNKNOWN_CATEGORY)


def classify_path(path: str | Path) -> dict[str, str]:
    path_obj = Path(path)
    suffix = path_obj.suffix.lower()
    category = classify_suffix(suffix)
    return {
        "suffix": suffix,
        "category": category,
    }


def summarize_categories(files: list[dict]) -> dict[str, int]:
    counts = Counter()

    for file_record in files:
        category = file_record.get("category", UNKNOWN_CATEGORY)
        counts[category] += 1

    return dict(sorted(counts.items()))
