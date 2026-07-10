from pathlib import Path


def test_volatility_filtered_sma_script_exists():
    script_path = Path("scripts/run_volatility_filtered_sma_backtest.py")

    assert script_path.exists()


def test_volatility_filtered_sma_script_references_outputs():
    script_path = Path("scripts/run_volatility_filtered_sma_backtest.py")
    text = script_path.read_text()

    assert "volatility_filtered_sma_results.csv" in text
    assert "volatility_filtered_sma_summary.csv" in text
    assert "VolatilityFilteredSMAConfig" in text
