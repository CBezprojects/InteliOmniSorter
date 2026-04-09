from src.actions.dry_run_executor import build_dry_run_actions


def test_build_dry_run_actions():
    validation_result = {
        "scan_path": "/tmp/test",
        "total_files": 2,
        "summary": {"by_category": {"code": 1, "document": 1}},
        "safety_summary": {"safe": 1, "conflicts": 1, "blocked": 1},
        "git_protection": {
            "active": False,
            "repo_root": None,
            "protected": {},
            "summary": {
                "protected_total": 0,
                "untracked": 0,
                "modified": 0,
                "staged": 0,
            },
        },
        "plan": [
            {
                "source": "/tmp/test/a.py",
                "destination": "/tmp/test/Code/python/a.py",
                "safe": True,
                "reason": "",
                "status": "safe",
            },
            {
                "source": "/tmp/test/b.pdf",
                "destination": "/tmp/test/Documents/pdf/b.pdf",
                "safe": False,
                "reason": "destination already exists",
                "status": "conflict",
            },
        ],
    }

    result = build_dry_run_actions(validation_result)

    assert result["scan_path"] == "/tmp/test"
    assert result["total_files"] == 2
    assert result["safety_summary"]["safe"] == 1
    assert result["safety_summary"]["blocked"] == 1
    assert result["git_protection"]["active"] is False
    assert len(result["actions"]) == 2

    assert result["actions"][0]["action"] == "move"
    assert result["actions"][0]["will_move"] is True

    assert result["actions"][1]["action"] == "blocked"
    assert result["actions"][1]["will_move"] is False
