from pathlib import Path


def test_risk_limits_script_exists():
    script_path = Path("scripts/create_risk_limits_report.py")

    assert script_path.exists()


def test_risk_limits_script_references_outputs():
    script_path = Path("scripts/create_risk_limits_report.py")
    text = script_path.read_text()

    assert "risk_limits_report.json" in text
    assert "risk_limits_report.md" in text
    assert "strategy_decision_gate.json" in text
