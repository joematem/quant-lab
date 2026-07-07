from __future__ import annotations

import pandas as pd

from quantlab.research_performance import summarize_performance


def create_buy_and_hold_returns(backtest_results: pd.DataFrame) -> pd.DataFrame:
    """Create buy-and-hold returns from backtest price data."""
    required_columns = {"ticker", "date", "adj_close", "asset_return"}
    missing = required_columns - set(backtest_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    benchmark = backtest_results[["ticker", "date", "adj_close", "asset_return"]].copy()

    benchmark["strategy"] = "buy_and_hold"
    benchmark["daily_return"] = benchmark["asset_return"].fillna(0.0)

    return benchmark[["ticker", "strategy", "date", "adj_close", "daily_return"]]


def create_strategy_returns(backtest_results: pd.DataFrame) -> pd.DataFrame:
    """Create strategy returns from backtest output."""
    required_columns = {"ticker", "date", "adj_close", "strategy_net_return"}
    missing = required_columns - set(backtest_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    strategy = backtest_results[
        ["ticker", "date", "adj_close", "strategy_net_return"]
    ].copy()

    strategy["strategy"] = "sma_crossover"
    strategy["daily_return"] = strategy["strategy_net_return"].fillna(0.0)

    return strategy[["ticker", "strategy", "date", "adj_close", "daily_return"]]


def compare_strategy_to_buy_and_hold(
    backtest_results: pd.DataFrame,
) -> pd.DataFrame:
    """Combine SMA strategy returns with buy-and-hold returns."""
    strategy_returns = create_strategy_returns(backtest_results)
    benchmark_returns = create_buy_and_hold_returns(backtest_results)

    comparison = pd.concat(
        [strategy_returns, benchmark_returns],
        ignore_index=True,
    )

    comparison["cumulative_return"] = comparison.groupby("strategy")[
        "daily_return"
    ].transform(lambda x: (1 + x).cumprod() - 1)

    return comparison.sort_values(["strategy", "date"]).reset_index(drop=True)


def summarize_strategy_comparison(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize strategy and benchmark performance."""
    required_columns = {"ticker", "strategy", "date", "adj_close", "daily_return"}
    missing = required_columns - set(comparison.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    summaries = []

    for strategy_name, group in comparison.groupby("strategy"):
        summary_input = group[["ticker", "date", "adj_close", "daily_return"]].copy()

        summary = summarize_performance(summary_input)
        summary.insert(1, "strategy", strategy_name)
        summaries.append(summary)

    result = pd.concat(summaries, ignore_index=True)
    return result.sort_values("strategy").reset_index(drop=True)
