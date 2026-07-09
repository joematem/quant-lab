import pandas as pd
import pytest

from quantlab.risk.monte_carlo import (
    run_return_bootstrap_monte_carlo,
    summarize_monte_carlo_results,
)


def sample_returns() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["equal_weight_sma"] * 10,
            "date": pd.date_range("2024-01-01", periods=10, freq="B"),
            "daily_return": [
                0.01,
                -0.005,
                0.002,
                0.004,
                -0.003,
                0.006,
                -0.002,
                0.003,
                0.001,
                -0.004,
            ],
        }
    )


def test_run_return_bootstrap_monte_carlo_returns_simulations():
    result = run_return_bootstrap_monte_carlo(
        returns=sample_returns(),
        simulations=25,
        seed=42,
        output_ticker="equal_weight_sma_monte_carlo",
    )

    assert len(result) == 25
    assert set(result["ticker"]) == {"equal_weight_sma_monte_carlo"}
    assert "total_return" in result.columns
    assert "max_drawdown" in result.columns


def test_summarize_monte_carlo_results_returns_probability_columns():
    results = run_return_bootstrap_monte_carlo(
        returns=sample_returns(),
        simulations=25,
        seed=42,
        output_ticker="equal_weight_sma_monte_carlo",
    )

    summary = summarize_monte_carlo_results(results)

    assert not summary.empty
    assert "probability_positive_return" in summary.columns
    assert "probability_drawdown_worse_than_30pct" in summary.columns


def test_run_return_bootstrap_monte_carlo_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        run_return_bootstrap_monte_carlo(
            returns=bad_data,
            simulations=10,
            seed=42,
            output_ticker="bad",
        )
