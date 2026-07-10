import pandas as pd
import pytest

from quantlab.backtesting.volatility_filtered_sma import (
    VolatilityFilteredSMAConfig,
    add_realized_volatility,
    generate_volatility_filtered_sma_signals,
    run_volatility_filtered_sma_backtest,
    summarize_volatility_filtered_sma_backtest,
)


def sample_prices() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=120, freq="B")
    prices = [100 + index * 0.5 for index in range(120)]

    return pd.DataFrame(
        {
            "ticker": ["AAPL"] * 120,
            "date": dates,
            "adj_close": prices,
        }
    )


def test_add_realized_volatility_adds_column():
    result = add_realized_volatility(sample_prices(), lookback=20)

    assert "realized_annualized_volatility" in result.columns
    assert "asset_return" in result.columns


def test_add_realized_volatility_rejects_invalid_lookback():
    with pytest.raises(ValueError, match="lookback must be greater than 1"):
        add_realized_volatility(sample_prices(), lookback=1)


def test_generate_volatility_filtered_sma_signals_adds_filter_columns():
    result = generate_volatility_filtered_sma_signals(
        sample_prices(),
        short_window=5,
        long_window=20,
        volatility_lookback=20,
        max_annualized_volatility=0.40,
    )

    assert "volatility_filter" in result.columns
    assert "filtered_signal" in result.columns
    assert "position" in result.columns


def test_generate_volatility_filtered_sma_rejects_invalid_volatility_threshold():
    with pytest.raises(
        ValueError,
        match="max_annualized_volatility must be positive",
    ):
        generate_volatility_filtered_sma_signals(
            sample_prices(),
            short_window=5,
            long_window=20,
            volatility_lookback=20,
            max_annualized_volatility=0.0,
        )


def test_run_volatility_filtered_sma_backtest_returns_results():
    config = VolatilityFilteredSMAConfig(
        ticker="AAPL",
        short_window=5,
        long_window=20,
        volatility_lookback=20,
        max_annualized_volatility=0.40,
        transaction_cost_bps=5.0,
    )

    result = run_volatility_filtered_sma_backtest(sample_prices(), config)

    assert not result.empty
    assert "strategy_net_return" in result.columns
    assert "cumulative_return" in result.columns
    assert set(result["ticker"]) == {"AAPL"}


def test_summarize_volatility_filtered_sma_backtest_returns_summary():
    config = VolatilityFilteredSMAConfig(
        ticker="AAPL",
        short_window=5,
        long_window=20,
        volatility_lookback=20,
        max_annualized_volatility=0.40,
        transaction_cost_bps=5.0,
    )

    results = run_volatility_filtered_sma_backtest(sample_prices(), config)
    summary = summarize_volatility_filtered_sma_backtest(results)

    assert not summary.empty
    assert "average_volatility_filter" in summary.columns
    assert "average_realized_annualized_volatility" in summary.columns
