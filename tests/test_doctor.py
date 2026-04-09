from src.safety.doctor import run_doctor


def test_doctor_returns_summary() -> None:
    result = run_doctor()
    assert "summary" in result
    assert "checks" in result
    assert result["summary"]["total"] >= 1
