from pathlib import Path


def test_full_experiment_runner_includes_cost_stress_step():
    script_path = Path("scripts/run_full_sma_research_experiment.py")
    text = script_path.read_text()

    assert "scripts/run_transaction_cost_stress_test.py" in text
    assert "--costs-bps" in text


def test_report_script_includes_cost_stress_summary():
    script_path = Path("scripts/create_sma_research_report.py")
    text = script_path.read_text()

    assert "transaction_cost_stress_summary.csv" in text
