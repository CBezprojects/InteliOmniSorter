import argparse
import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

from PIL import Image, ExifTags
import imagehash
from PyPDF2 import PdfReader
from tqdm import tqdm

# Optional imports (may fail gracefully)
try:
    import face_recognition
except Exception:
    face_recognition = None

try:
    import pytesseract
except Exception:
    pytesseract = None


IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".tif", ".tiff", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".m4v", ".3gp"}
DOC_EXT   = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".rtf", ".txt"}
CODE_EXT  = {".py", ".ps1", ".psm1", ".java", ".cs", ".cpp", ".h", ".js", ".ts",
             ".html", ".css", ".json", ".yml", ".yaml", ".gradle", ".kts"}
INSTALLER_EXT = {".exe", ".msi", ".msix", ".apk", ".iso", ".img", ".dmg", ".cab", ".msixbundle", ".zip"}

STUDY_KEYWORDS = [
    "unisa", "assignment", "ass1", "ass2", "ass3",
    "exam", "portfolio",
    "age", "anh", "soc", "dva", "cls"
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


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, help="Path to Master_Cloud")
    return p.parse_args()


def get_env_tools():
    return {
        "exiftool":  os.environ.get("SMARTBRAIN_EXIFTOOL") or "exiftool",
        "ffprobe":   os.environ.get("SMARTBRAIN_FFPROBE")  or "ffprobe",
        "tesseract": os.environ.get("SMARTBRAIN_TESSERACT")or "tesseract",
    }


# --------------- SQLITE DB ---------------

def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        src TEXT NOT NULL,
        dst TEXT NOT NULL,
        category TEXT,
        hash TEXT,
        notes TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        category TEXT,
        hash TEXT,
        person_id INTEGER,
        created_ts TEXT,
        device TEXT,
        meta_json TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        notes TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        context TEXT,
        message TEXT
    )
    """)
    conn.commit()
    return conn


def db_log_move(conn, src: Path, dst: Path, category: str, h: str | None, notes: str = ""):
    ts = datetime.now().isoformat(timespec="seconds")
    c = conn.cursor()
    c.execute("INSERT INTO moves(ts, src, dst, category, hash, notes) VALUES(?,?,?,?,?,?)",
              (ts, str(src), str(dst), category, h or "", notes))
    conn.commit()


def db_log_error(conn, context: str, msg: str):
    ts = datetime.now().isoformat(timespec="seconds")
    c = conn.cursor()
    c.execute("INSERT INTO errors(ts, context, message) VALUES(?,?,?)", (ts, context, msg))
    conn.commit()


# --------------- UTILITIES ---------------

def ensure_category_dirs(root: Path):
    for name in CATEGORY_DIRS.values():
        (root / name).mkdir(parents=True, exist_ok=True)


def move_with_dedup(src: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / src.name
    if not target.exists():
        src.replace(target)
        return target
    stem = target.stem
    suffix = target.suffix
    i = 1
    while True:
        cand = dest_dir / f"{stem}__{i}{suffix}"
        if not cand.exists():
            src.replace(cand)
            return cand
        i += 1


def hash_image(path: Path):
    try:
        with Image.open(path) as img:
            return str(imagehash.average_hash(img))
    except Exception:
        return None


# --------------- METADATA: EXIF / EXIFTOOL / FFPROBE / OCR ---------------

def exiftool_metadata(exiftool_cmd: str, path: Path) -> dict:
    """Call exiftool, return key:value dict. If fails, return {}."""
    try:
        result = subprocess.run(
            [exiftool_cmd, "-j", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=8
        )
        if result.returncode != 0 or not result.stdout.strip():
            return {}
        import json
        data = json.loads(result.stdout)[0]
        return data
    except Exception:
        return {}


def ffprobe_metadata(ffprobe_cmd: str, path: Path) -> dict:
    """Call ffprobe JSON for video, parse minimal info."""
    try:
        result = subprocess.run(
            [ffprobe_cmd, "-v", "error", "-show_entries",
             "format=duration:stream=codec_name,codec_type,width,height",
             "-of", "json", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=8
        )
        if result.returncode != 0 or not result.stdout.strip():
            return {}
        import json
        data = json.loads(result.stdout)
        out = {}
        fmt = data.get("format", {})
        out["duration"] = fmt.get("duration")
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                out["v_codec"] = s.get("codec_name")
                out["width"] = s.get("width")
                out["height"] = s.get("height")
        return out
    except Exception:
        return {}


def ocr_image_for_studies(path: Path) -> bool:
    """Use Tesseract (if available) to detect study text inside images."""
    if pytesseract is None:
        return False
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img, lang="eng").lower()
        for kw in STUDY_KEYWORDS:
            if kw in text:
                return True
    except Exception:
        return False
    return False


def exif_basic_from_pillow(path: Path):
    try:
        img = Image.open(path)
        exif = img._getexif() or {}
        md = {}
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            md[tag] = value
        dt_str = md.get("DateTimeOriginal") or md.get("DateTime")
        year = None
        month = None
        if dt_str:
            parts = dt_str.split(" ")[0].replace(":", "-")
            try:
                dt_parsed = datetime.fromisoformat(parts)
                year, month = dt_parsed.year, dt_parsed.month
            except ValueError:
                pass
        if not year or not month:
            ts = path.stat().st_mtime
            dt = datetime.fromtimestamp(ts)
            year, month = dt.year, dt.month
        device = md.get("Model") or md.get("Make") or "UnknownDevice"
        if isinstance(device, bytes):
            device = device.decode("utf-8", errors="ignore")
        return year, month, str(device).strip().replace(" ", "_")[:40]
    except Exception:
        ts = path.stat().st_mtime
        dt = datetime.fromtimestamp(ts)
        return dt.year, dt.month, "UnknownDevice"


# --------------- CLASSIFICATION ---------------

def classify_doc_by_content_pdf(file_path: Path) -> str | None:
    if file_path.suffix.lower() != ".pdf":
        return None
    try:
        reader = PdfReader(str(file_path))
        text_low = ""
        for page in reader.pages[:3]:
            text_low += (page.extract_text() or "").lower() + " "
        for kw in STUDY_KEYWORDS:
            if kw in text_low:
                return "Studies"
    except Exception:
        return None
    return None


def classify_file(root: Path, file_path: Path) -> str:
    ext = file_path.suffix.lower()
    full = str(file_path).lower()
    name = file_path.name.lower()

    if ext in INSTALLER_EXT or "\\installers\\" in full:
        return "Installers"

    if ext in IMAGE_EXT:
        # later: differentiate Screenshots vs Photos vs People candidates
        return "Photos"

    if ext in VIDEO_EXT:
        return "Videos"

    if ext in DOC_EXT:
        for kw in STUDY_KEYWORDS:
            if kw in name:
                return "Studies"
        cat = classify_doc_by_content_pdf(file_path)
        if cat:
            return cat

    if ext in CODE_EXT or any(k in full for k in ["\\dev\\", "\\minecraft", "battery_pro", "uilnes", "embassy_contact_scraper"]):
        return "Projects"

    if any(k in full for k in ["backup", "whatsapp", "recover", "sdcard", "ouma hardeskyf"]):
        return "Backups"

    if ext in DOC_EXT:
        return "Documents"

    return "Archive"


# --------------- MAIN SCAN & SORT ---------------

def main():
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Root path not found: {root}")
        sys.exit(1)

    tools = get_env_tools()
    db_path = root / "_SmartSorter" / "smartbrain.db"
    conn = init_db(db_path)

    ensure_category_dirs(root)

    category_paths = [root / d for d in CATEGORY_DIRS.values()]
    skip_roots = category_paths + [root / "_SortLogs", root / "_SmartSorter"]

    all_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        # skip category / system dirs
        if any(str(current_dir).startswith(str(s)) for s in skip_roots):
            dirnames[:] = []
            continue
        for name in filenames:
            all_files.append(current_dir / name)

    print(f"[SmartBrain] Found {len(all_files)} files to consider.")

    seen_hashes = {}

    for p in tqdm(all_files, desc="SmartBrain sorting"):
        ext = p.suffix.lower()

        img_hash = None
        # duplicate detection for images
        if ext in IMAGE_EXT:
            img_hash = hash_image(p)
            if img_hash is not None:
                if img_hash in seen_hashes:
                    # duplicate → Archive/Duplicates
                    dup_dir = root / CATEGORY_DIRS["Archive"] / "Duplicates"
                    final = move_with_dedup(p, dup_dir)
                    db_log_move(conn, p, final, "Archive", img_hash, notes="duplicate")
                    continue
                else:
                    seen_hashes[img_hash] = p

        # classify
        cat = classify_file(root, p)
        dest_base = root / CATEGORY_DIRS.get(cat, CATEGORY_DIRS["Archive"])

        # extra: for images, send study-looking screenshots to Studies
        if cat == "Photos" and pytesseract is not None:
            try:
                if ocr_image_for_studies(p):
                    dest_base = root / CATEGORY_DIRS["Studies"]
                    cat = "Studies"
            except Exception as e:
                db_log_error(conn, "OCR_STUDIES", f"{p}: {e}")

        # refine destination structure
        if cat == "Photos" and ext in IMAGE_EXT:
            year, month, device = exif_basic_from_pillow(p)
            dest = dest_base / str(year) / f"{month:02d}" / device
        elif cat == "Videos" and ext in VIDEO_EXT:
            ts = p.stat().st_mtime
            dt = datetime.fromtimestamp(ts)
            dest = dest_base / str(dt.year) / f"{dt.month:02d}"
        else:
            dest = dest_base

        try:
            final = move_with_dedup(p, dest)
            db_log_move(conn, p, final, cat, img_hash)
        except Exception as e:
            print(f"[ERROR] Failed to move {p}: {e}")
            db_log_error(conn, "MOVE", f"{p}: {e}")

    print("[SmartBrain] Done.")


if __name__ == "__main__":
    main()
