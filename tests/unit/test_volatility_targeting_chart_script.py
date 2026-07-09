from pathlib import Path


def test_volatility_targeting_chart_script_exists():
    script_path = Path("scripts/create_volatility_targeting_charts.py")

    assert script_path.exists()


def test_volatility_targeting_chart_script_references_required_outputs():
    script_path = Path("scripts/create_volatility_targeting_charts.py")
    text = script_path.read_text()

    assert "portfolio_equal_weight_returns.csv" in text
    assert "portfolio_volatility_targeted_returns.csv" in text
    assert "portfolio_volatility_targeted_comparison.png" in text
