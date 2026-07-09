from pathlib import Path


def test_full_experiment_runner_includes_cost_stress_chart_step():
    script_path = Path("scripts/run_full_sma_research_experiment.py")
    text = script_path.read_text()

    assert "scripts/create_transaction_cost_stress_charts.py" in text
