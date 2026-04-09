from pathlib import Path

from src.safety.validator import validate_plan


def test_validate_plan_marks_safe(tmp_path: Path):
    plan_result = {
        "scan_path": str(tmp_path),
        "total_files": 1,
        "summary": {"by_category": {"code": 1}, "by_subtype": {"code::python": 1}},
        "plan": [
            {
                "source": str(tmp_path / "a.py"),
                "name": "a.py",
                "category": "code",
                "subtype": "python",
                "destination": str(tmp_path / "Code" / "python" / "a.py"),
            }
        ],
    }

    result = validate_plan(plan_result)

    assert result["safety_summary"]["safe"] == 1
    assert result["safety_summary"]["conflicts"] == 0
    assert result["plan"][0]["status"] == "safe"


def test_validate_plan_marks_conflict(tmp_path: Path):
    dest = tmp_path / "Code" / "python"
    dest.mkdir(parents=True)
    (dest / "a.py").write_text("x", encoding="utf-8")

    plan_result = {
        "scan_path": str(tmp_path),
        "total_files": 1,
        "summary": {"by_category": {"code": 1}, "by_subtype": {"code::python": 1}},
        "plan": [
            {
                "source": str(tmp_path / "src" / "a.py"),
                "name": "a.py",
                "category": "code",
                "subtype": "python",
                "destination": str(dest / "a.py"),
            }
        ],
    }

    result = validate_plan(plan_result)

    assert result["safety_summary"]["safe"] == 0
    assert result["safety_summary"]["conflicts"] == 1
    assert result["plan"][0]["status"] == "conflict"
    assert result["plan"][0]["safe"] is False
