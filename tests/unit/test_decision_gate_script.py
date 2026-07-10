from pathlib import Path


def test_decision_gate_script_exists():
    script_path = Path("scripts/create_strategy_decision_gate.py")

    assert script_path.exists()


def test_decision_gate_script_references_outputs():
    script_path = Path("scripts/create_strategy_decision_gate.py")
    text = script_path.read_text()

    assert "strategy_decision_gate.json" in text
    assert "strategy_decision_gate.md" in text
