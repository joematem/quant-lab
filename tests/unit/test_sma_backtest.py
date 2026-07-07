import pandas as pd
import pytest

from quantlab.backtesting.sma import (
    SMABacktestConfig,
    generate_sma_signals,
    run_sma_backtest,
    summarize_sma_backtest,
)


def sample_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL"] * 8,
            "date": pd.date_range("2024-01-01", periods=8, freq="D"),
            "adj_close": [100, 101, 102, 103, 104, 103, 102, 101],
        }
    )


def test_generate_sma_signals_creates_position_column():
    prices = sample_prices()
    result = generate_sma_signals(prices, short_window=2, long_window=3)

    assert "short_sma" in result.columns
    assert "long_sma" in result.columns
    assert "signal" in result.columns
    assert "position" in result.columns


def test_run_sma_backtest_uses_shifted_positions():
    prices = sample_prices()
    config = SMABacktestConfig(
        ticker="AAPL",
        short_window=2,
        long_window=3,
        transaction_cost_bps=5.0,
    )

    result = run_sma_backtest(prices, config)

    assert "strategy_net_return" in result.columns
    assert result["position"].iloc[0] == 0.0


def test_generate_sma_signals_rejects_invalid_windows():
    prices = sample_prices()

    with pytest.raises(ValueError, match="short_window must be less than long_window"):
        generate_sma_signals(prices, short_window=5, long_window=5)


def test_summarize_sma_backtest_returns_summary():
    prices = sample_prices()
    config = SMABacktestConfig(
        ticker="AAPL",
        short_window=2,
        long_window=3,
        transaction_cost_bps=5.0,
    )

    results = run_sma_backtest(prices, config)
    summary = summarize_sma_backtest(results)

    assert len(summary) == 1
    assert summary["ticker"].iloc[0] == "AAPL"
    assert "trade_count" in summary.columns
    assert "average_exposure" in summary.columns
