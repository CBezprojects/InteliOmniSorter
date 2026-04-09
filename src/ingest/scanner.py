from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import hashlib
import json
import os


@dataclass
class FileRecord:
    path: str
    name: str
    extension: str
    size: int
    sha256_head: str
    is_dir: bool


def sha256_head(path: Path, bytes_to_read: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        chunk = f.read(bytes_to_read)
        h.update(chunk)
    return h.hexdigest()


def scan_paths(root: Path) -> Iterable[FileRecord]:
    for item in root.rglob("*"):
        try:
            stat = item.stat()
            yield FileRecord(
                path=str(item.resolve()),
                name=item.name,
                extension=item.suffix.lower(),
                size=stat.st_size,
                sha256_head=sha256_head(item) if item.is_file() else "",
                is_dir=item.is_dir(),
            )
        except Exception:
            continue


def write_report(root: Path, output_file: Path) -> int:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_file.open("w", encoding="utf-8") as f:
        for record in scan_paths(root):
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            count += 1
    return count


if __name__ == "__main__":
    target = Path(os.environ.get("OMNI_SCAN_PATH", ".")).resolve()
    out = Path("logs/ingest_scan.jsonl")
    count = write_report(target, out)
    print(f"[OMNI] Scan complete. {count} records written to {out}")
