from pathlib import Path


def test_cost_stress_chart_script_exists():
    script_path = Path("scripts/create_transaction_cost_stress_charts.py")

    assert script_path.exists()


def test_cost_stress_chart_script_references_outputs():
    script_path = Path("scripts/create_transaction_cost_stress_charts.py")
    text = script_path.read_text()

    assert "transaction_cost_stress_summary.csv" in text
    assert "transaction_cost_stress_sharpe.png" in text
    assert "transaction_cost_stress_total_return_decay.png" in text
