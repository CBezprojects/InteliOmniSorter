from pathlib import Path
from unittest.mock import patch

from src.safety.validator import validate_plan


@patch("src.safety.validator.build_git_protection_map")
def test_validator_blocks_git_protected_file(mock_git_map, tmp_path: Path):
    source = tmp_path / "src" / "demo.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("print('hi')", encoding="utf-8")

    destination = tmp_path / "Code" / "python" / "demo.py"

    mock_git_map.return_value = {
        "active": True,
        "repo_root": str(tmp_path),
        "protected": {
            "src/demo.py": {
                "git_status": "??",
                "reason": "git untracked file",
            }
        },
        "summary": {
            "protected_total": 1,
            "untracked": 1,
            "modified": 0,
            "staged": 0,
        },
    }

    plan_result = {
        "scan_path": str(tmp_path),
        "total_files": 1,
        "summary": {"by_category": {"code": 1}, "by_type": {"code::python": 1}},
        "plan": [
            {
                "source": str(source),
                "destination": str(destination),
                "category": "code",
                "subtype": "python",
            }
        ],
    }

    result = validate_plan(plan_result)

    assert result["safety_summary"]["blocked"] == 1
    assert result["plan"][0]["status"] == "blocked"
    assert result["plan"][0]["reason"] == "git untracked file"


@patch("src.safety.validator.build_git_protection_map")
def test_validator_marks_safe_when_no_git_or_conflict(mock_git_map, tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")
    destination = tmp_path / "Documents" / "text" / "notes.txt"

    mock_git_map.return_value = {
        "active": False,
        "repo_root": None,
        "protected": {},
        "summary": {
            "protected_total": 0,
            "untracked": 0,
            "modified": 0,
            "staged": 0,
        },
    }

    plan_result = {
        "scan_path": str(tmp_path),
        "total_files": 1,
        "summary": {"by_category": {"document": 1}, "by_type": {"document::text": 1}},
        "plan": [
            {
                "source": str(source),
                "destination": str(destination),
                "category": "document",
                "subtype": "text",
            }
        ],
    }

    result = validate_plan(plan_result)

    assert result["safety_summary"]["safe"] == 1
    assert result["plan"][0]["status"] == "safe"
