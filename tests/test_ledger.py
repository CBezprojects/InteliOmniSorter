from src.actions.ledger import create_batch_record


def test_create_batch_record():
    action_result = {
        "scan_path": "/tmp/test",
        "total_files": 1,
        "safety_summary": {"safe": 1, "conflicts": 0, "blocked": 0},
        "directory_plan": ["/tmp/test/Code/python"],
        "actions": [
            {
                "source": "/tmp/test/a.py",
                "destination": "/tmp/test/Code/python/a.py",
                "category": "code",
                "subtype": "python",
                "status": "safe",
                "reason": "",
                "action": "move",
                "mode": "dry-run",
                "will_move": True,
            }
        ],
    }

    batch = create_batch_record(action_result)

    assert batch["mode"] == "dry-run"
    assert batch["total_files"] == 1
    assert len(batch["items"]) == 1
    assert batch["items"][0]["source"] == "/tmp/test/a.py"
