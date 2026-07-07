import pandas as pd
import pytest

from quantlab.backtesting.parameter_sweep import run_sma_parameter_sweep


def sample_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL"] * 20,
            "date": pd.date_range("2024-01-01", periods=20, freq="D"),
            "adj_close": [
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                108,
                107,
                106,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
            ],
        }
    )


def test_run_sma_parameter_sweep_returns_ranked_results():
    result = run_sma_parameter_sweep(
        prices=sample_prices(),
        ticker="AAPL",
        short_windows=[2, 3],
        long_windows=[5, 6],
        transaction_cost_bps=5.0,
    )

    assert not result.empty
    assert "short_window" in result.columns
    assert "long_window" in result.columns
    assert "sharpe_ratio" in result.columns
    assert set(result["ticker"]) == {"AAPL"}


def test_run_sma_parameter_sweep_rejects_no_valid_combinations():
    with pytest.raises(ValueError, match="No valid SMA parameter combinations"):
        run_sma_parameter_sweep(
            prices=sample_prices(),
            ticker="AAPL",
            short_windows=[10],
            long_windows=[5],
            transaction_cost_bps=5.0,
        )
