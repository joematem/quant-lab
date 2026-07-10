from pathlib import Path


def test_report_script_loads_monte_carlo_summary():
    script_path = Path("scripts/create_sma_research_report.py")
    text = script_path.read_text()

    assert "monte_carlo_portfolio_summary.csv" in text
    assert "monte_carlo_summary=monte_carlo_summary" in text
