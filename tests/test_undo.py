from pathlib import Path

from src.actions.ledger import load_ledger, save_ledger
from src.actions.undo import get_latest_applied_batch, undo_batch


def test_undo_batch_restores_file(tmp_path: Path):
    original_source = tmp_path / "a.py"
    moved_destination = tmp_path / "Code" / "python" / "a.py"
    moved_destination.parent.mkdir(parents=True, exist_ok=True)
    moved_destination.write_text("print('hi')", encoding="utf-8")

    batch = {
        "batch_id": "batch-undo-1",
        "timestamp": "2026-01-01T00:00:00",
        "mode": "applied",
        "scan_path": str(tmp_path),
        "total_files": 1,
        "safety_summary": {"safe": 1, "conflicts": 0, "blocked": 0},
        "directory_plan": [str(moved_destination.parent)],
        "items": [
            {
                "source": str(original_source),
                "destination": str(moved_destination),
                "category": "code",
                "subtype": "python",
                "status": "safe",
                "reason": "",
                "action": "move",
                "mode": "dry-run",
                "will_move": True,
                "execution_status": "applied",
                "execution_reason": "",
            }
        ],
        "execution_summary": {"applied": 1, "blocked": 0, "failed": 0, "total": 1},
    }

    save_ledger([batch])

    latest = get_latest_applied_batch()
    assert latest is not None

    result = undo_batch(latest)

    assert result["mode"] == "undone"
    assert result["undo_summary"]["reverted"] == 1
    assert original_source.exists()
    assert not moved_destination.exists()

    stored = load_ledger()[0]
    assert stored["items"][0]["undo_status"] == "reverted"
