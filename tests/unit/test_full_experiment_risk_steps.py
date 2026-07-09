from pathlib import Path


def test_full_experiment_runner_includes_risk_steps():
    script_path = Path("scripts/run_full_sma_research_experiment.py")
    text = script_path.read_text()

    assert "scripts/run_portfolio_volatility_targeting.py" in text
    assert "scripts/create_volatility_targeting_charts.py" in text


def test_report_script_includes_volatility_targeted_summary():
    script_path = Path("scripts/create_sma_research_report.py")
    text = script_path.read_text()

    assert "portfolio_volatility_targeted_summary.csv" in text
