from pathlib import Path

from src.actions.executor import apply_batch
from src.actions.ledger import load_ledger, save_ledger


def test_apply_batch_moves_safe_file(tmp_path: Path):
    source = tmp_path / "a.py"
    source.write_text("print('hi')", encoding="utf-8")

    destination = tmp_path / "Code" / "python" / "a.py"

    batch = {
        "batch_id": "batch-1",
        "timestamp": "2026-01-01T00:00:00",
        "mode": "dry-run",
        "scan_path": str(tmp_path),
        "total_files": 1,
        "safety_summary": {"safe": 1, "conflicts": 0, "blocked": 0},
        "directory_plan": [str(destination.parent)],
        "items": [
            {
                "source": str(source),
                "destination": str(destination),
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

    save_ledger([batch])

    result = apply_batch("batch-1")

    assert result["mode"] == "applied"
    assert result["execution_summary"]["applied"] == 1
    assert not source.exists()
    assert destination.exists()

    stored = load_ledger()[0]
    assert stored["items"][0]["execution_status"] == "applied"
