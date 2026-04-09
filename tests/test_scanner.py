from pathlib import Path

from src.ingest.scanner import scan_directory


def test_scan_directory_finds_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.jpg").write_text("x", encoding="utf-8")

    result = scan_directory(str(tmp_path))

    assert result["file_count"] == 2
    names = {item["name"] for item in result["files"]}
    assert "a.txt" in names
    assert "b.jpg" in names
