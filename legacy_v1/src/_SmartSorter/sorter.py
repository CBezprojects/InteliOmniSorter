import argparse
import os
import sys
import csv
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags
import imagehash
from PyPDF2 import PdfReader


def parse_args():
    p = argparse.ArgumentParser(description="Smart Master_Cloud sorter")
    p.add_argument("--root", required=True, help="Path to Master_Cloud root")
    return p.parse_args()


IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".tif", ".tiff", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".m4v", ".3gp"}
DOC_EXT   = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".rtf", ".txt"}
CODE_EXT  = {".py", ".ps1", ".psm1", ".java", ".cs", ".cpp", ".h", ".js", ".ts",
             ".html", ".css", ".json", ".yml", ".yaml", ".gradle", ".kts"}
INSTALLER_EXT = {".exe", ".msi", ".msix", ".apk", ".iso", ".img", ".dmg", ".cab", ".msixbundle", ".zip"}

STUDY_KEYWORDS = [
    "unisa", "assignment", "ass1", "ass2", "ass3",
    "exam", "portfolio",
    "age", "anh", "soc", "dva", "cls"  # module code roots
]

CATEGORY_DIRS = {
    "Studies":   "01_Studies",
    "People":    "02_People",
    "Photos":    "03_Photos",
    "Videos":    "04_Videos",
    "Projects":  "05_Projects",
    "Installers":"06_Installers",
    "Documents": "07_Documents",
    "Backups":   "08_Backups",
    "Archive":   "99_Archive",
}


def ensure_category_dirs(root: Path):
    for name in CATEGORY_DIRS.values():
        (root / name).mkdir(parents=True, exist_ok=True)


def init_log(root: Path) -> Path:
    log_dir = root / "_SortLogs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"moves_{ts}.csv"
    with log_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "original_path", "new_path"])
    return log_path


def write_move_log(log_path: Path, src: Path, dst: Path):
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            str(src),
            str(dst),
        ])


def is_under_any(path: Path, roots):
    """Check if path is under any of the given root directories."""
    for r in roots:
        try:
            path.relative_to(r)
            return True
        except ValueError:
            continue
    return False


def classify_doc_by_content(file_path: Path) -> str | None:
    """Extra brain for docs: use PDF text to detect Studies."""
    suffix = file_path.suffix.lower()
    if suffix != ".pdf":
        return None

    try:
        reader = PdfReader(str(file_path))
        text_chunks = []
        for page in reader.pages[:3]:
            t = page.extract_text() or ""
            text_chunks.append(t.lower())
        content = " ".join(text_chunks)
        for kw in STUDY_KEYWORDS:
            if kw in content:
                return "Studies"
    except Exception:
        # If PDF is weird, silently ignore and let normal classification handle it
        return None

    return None


def classify_file(root: Path, file_path: Path) -> str:
    """Return one of CATEGORY_DIRS keys."""
    ext = file_path.suffix.lower()
    full_lower = str(file_path).lower()
    name_lower = file_path.name.lower()

    # 1) Installers
    if ext in INSTALLER_EXT or "\\installers\\" in full_lower:
        return "Installers"

    # 2) Photos
    if ext in IMAGE_EXT:
        return "Photos"

    # 3) Videos
    if ext in VIDEO_EXT:
        return "Videos"

    # 4) Studies (by name first)
    if ext in DOC_EXT:
        for kw in STUDY_KEYWORDS:
            if kw in name_lower:
                return "Studies"
        # if not in name, try PDF content sniffing
        cat = classify_doc_by_content(file_path)
        if cat:
            return cat

    # 5) Projects (code / dev / specific dirs)
    if ext in CODE_EXT or any(key in full_lower for key in [
        "\\dev\\", "\\minecraft", "battery_pro", "uilnes", "embassy_contact_scraper", "lunospot", "lunobot"
    ]):
        return "Projects"

    # 6) Backups / dumps
    if any(key in full_lower for key in ["backup", "whatsapp", "recover", "sdcard", "ouma hardeskyf"]):
        return "Backups"

    # 7) Generic docs
    if ext in DOC_EXT:
        return "Documents"

    # 8) Fallback
    return "Archive"


def move_with_dedup(src: Path, dest_dir: Path) -> Path:
    """Move src into dest_dir, avoid overwriting, return final path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / src.name

    if not target.exists():
        src.replace(target)
        return target

    # If filename exists, append counter
    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}__{counter}{suffix}"
        if not candidate.exists():
            src.replace(candidate)
            return candidate
        counter += 1


def get_exif_datetime_and_device(image_path: Path):
    """Return (year, month, device_name or 'Unknown') from EXIF if possible."""
    try:
        img = Image.open(image_path)
        exif = img._getexif() or {}
        exif_data = {}
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

        # DateTimeOriginal or DateTime
        dt_str = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
        year = None
        month = None
        if dt_str:
            # formats like "2023:11:22 18:25:01"
            parts = dt_str.split(" ")
            if parts:
                date_part = parts[0].replace(":", "-")
                try:
                    dt = datetime.fromisoformat(date_part)
                    year = dt.year
                    month = dt.month
                except ValueError:
                    pass

        device = exif_data.get("Model") or exif_data.get("Make") or "UnknownDevice"
        if isinstance(device, bytes):
            device = device.decode("utf-8", errors="ignore")

        if not year or not month:
            # fall back to file modified time
            ts = image_path.stat().st_mtime
            dt = datetime.fromtimestamp(ts)
            year, month = dt.year, dt.month

        return year, month, str(device).strip().replace(" ", "_")[:40]
    except Exception:
        ts = image_path.stat().st_mtime
        dt = datetime.fromtimestamp(ts)
        return dt.year, dt.month, "UnknownDevice"


def hash_image(path: Path):
    try:
        with Image.open(path) as img:
            return imagehash.average_hash(img)
    except Exception:
        return None


def main():
    args = parse_args()
    root = Path(args.root).expanduser().resolve()

    if not root.exists():
        print(f"Root path not found: {root}")
        sys.exit(1)

    ensure_category_dirs(root)
    log_path = init_log(root)
    print(f"[INFO] Logging moves to: {log_path}")

    # directories to skip
    category_paths = [root / d for d in CATEGORY_DIRS.values()]
    skip_roots = category_paths + [root / "_SortLogs", root / "_SmartSorter"]

    # For duplicate detection: map hash -> first file seen
    seen_hashes = {}

    all_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        # skip category & system folders
        if is_under_any(current_dir, skip_roots):
            # prevent walking deeper
            dirnames[:] = []
            continue

        for name in filenames:
            p = current_dir / name
            all_files.append(p)

    total = len(all_files)
    print(f"[INFO] Found {total} files to consider.")

    processed = 0
    for p in all_files:
        processed += 1
        if processed % 50 == 0 or processed == total:
            percent = (processed / total) * 100
            print(f"[INFO] {processed}/{total} ({percent:.1f}%)")

        ext = p.suffix.lower()

        # Duplicate detection only for images
        if ext in IMAGE_EXT:
            h = hash_image(p)
            if h is not None:
                if h in seen_hashes:
                    # we found a near-duplicate: send to Archive/Duplicates
                    dup_dir = root / CATEGORY_DIRS["Archive"] / "Duplicates"
                    final = move_with_dedup(p, dup_dir)
                    write_move_log(log_path, p, final)
                    continue
                else:
                    seen_hashes[h] = p

        # Classify category
        cat = classify_file(root, p)
        cat_dir_name = CATEGORY_DIRS.get(cat, CATEGORY_DIRS["Archive"])
        dest_base = root / cat_dir_name

        # For photos: create Year/Month/Device
        if cat == "Photos" and ext in IMAGE_EXT:
            y, m, device = get_exif_datetime_and_device(p)
            dest = dest_base / str(y) / f"{m:02d}" / device
        # For videos: Year/Month
        elif cat == "Videos" and ext in VIDEO_EXT:
            ts = p.stat().st_mtime
            dt = datetime.fromtimestamp(ts)
            dest = dest_base / str(dt.year) / f"{dt.month:02d}"
        else:
            dest = dest_base

        try:
            final_path = move_with_dedup(p, dest)
            write_move_log(log_path, p, final_path)
        except Exception as e:
            print(f"[ERROR] Failed to move {p}: {e}", file=sys.stderr)

    print("[DONE] Smart sorting complete.")


if __name__ == "__main__":
    main()
