import pandas as pd
import pytest

from quantlab.backtesting.walk_forward import (
    WalkForwardConfig,
    run_sma_walk_forward_validation,
)


def sample_prices() -> pd.DataFrame:
    dates = pd.date_range("2015-01-01", "2022-12-31", freq="B")
    prices = [100 + i * 0.05 for i in range(len(dates))]

    return pd.DataFrame(
        {
            "ticker": ["AAPL"] * len(dates),
            "date": dates,
            "adj_close": prices,
        }
    )


def test_run_sma_walk_forward_validation_returns_windows():
    config = WalkForwardConfig(
        ticker="AAPL",
        train_years=3,
        test_years=1,
        short_windows=(2, 3),
        long_windows=(5, 6),
        transaction_cost_bps=5.0,
    )

    result = run_sma_walk_forward_validation(sample_prices(), config)

    assert not result.empty
    assert "selected_short_window" in result.columns
    assert "selected_long_window" in result.columns
    assert "test_sharpe_ratio" in result.columns


def test_run_sma_walk_forward_validation_rejects_missing_ticker():
    config = WalkForwardConfig(ticker="MSFT")

    with pytest.raises(ValueError, match="No price data found"):
        run_sma_walk_forward_validation(sample_prices(), config)
