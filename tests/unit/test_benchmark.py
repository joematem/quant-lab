import pandas as pd
import pytest

from quantlab.backtesting.benchmark import (
    compare_strategy_to_buy_and_hold,
    create_buy_and_hold_returns,
    create_strategy_returns,
    summarize_strategy_comparison,
)


def sample_backtest_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "adj_close": [100.0, 101.0, 102.0],
            "asset_return": [None, 0.01, 0.009901],
            "strategy_net_return": [0.0, 0.005, 0.004],
        }
    )


def test_create_buy_and_hold_returns():
    result = create_buy_and_hold_returns(sample_backtest_results())

    assert set(result["strategy"]) == {"buy_and_hold"}
    assert result["daily_return"].iloc[0] == 0.0


def test_create_strategy_returns():
    result = create_strategy_returns(sample_backtest_results())

    assert set(result["strategy"]) == {"sma_crossover"}
    assert "daily_return" in result.columns


def test_compare_strategy_to_buy_and_hold_contains_two_strategies():
    result = compare_strategy_to_buy_and_hold(sample_backtest_results())

    assert set(result["strategy"]) == {"sma_crossover", "buy_and_hold"}
    assert "cumulative_return" in result.columns


def test_summarize_strategy_comparison_returns_two_rows():
    comparison = compare_strategy_to_buy_and_hold(sample_backtest_results())
    summary = summarize_strategy_comparison(comparison)

    assert len(summary) == 2
    assert set(summary["strategy"]) == {"sma_crossover", "buy_and_hold"}


def test_create_buy_and_hold_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        create_buy_and_hold_returns(bad_data)
