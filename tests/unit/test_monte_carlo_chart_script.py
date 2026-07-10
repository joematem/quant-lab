from pathlib import Path


def test_monte_carlo_chart_script_exists():
    script_path = Path("scripts/create_monte_carlo_charts.py")

    assert script_path.exists()


def test_monte_carlo_chart_script_references_outputs():
    script_path = Path("scripts/create_monte_carlo_charts.py")
    text = script_path.read_text()

    assert "monte_carlo_portfolio_results.csv" in text
    assert "monte_carlo_total_return_distribution.png" in text
    assert "monte_carlo_max_drawdown_distribution.png" in text
    assert "monte_carlo_sharpe_distribution.png" in text
