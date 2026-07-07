from __future__ import annotations

import pandas as pd

from quantlab.backtesting.benchmark import (
    compare_strategy_to_buy_and_hold,
    summarize_strategy_comparison,
)
from quantlab.backtesting.sma import SMABacktestConfig, run_sma_backtest


def compare_multi_ticker_sma_to_buy_and_hold(
    prices_by_ticker: dict[str, pd.DataFrame],
    short_window: int = 20,
    long_window: int = 50,
    transaction_cost_bps: float = 5.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare SMA crossover to buy-and-hold across multiple tickers."""
    all_comparisons = []
    all_summaries = []

    for ticker, prices in prices_by_ticker.items():
        config = SMABacktestConfig(
            ticker=ticker,
            short_window=short_window,
            long_window=long_window,
            transaction_cost_bps=transaction_cost_bps,
        )

        backtest_results = run_sma_backtest(prices, config)
        comparison = compare_strategy_to_buy_and_hold(backtest_results)
        summary = summarize_strategy_comparison(comparison)

        all_comparisons.append(comparison)
        all_summaries.append(summary)

    combined_comparison = pd.concat(all_comparisons, ignore_index=True)
    combined_summary = pd.concat(all_summaries, ignore_index=True)

    combined_summary = combined_summary.sort_values(
        ["ticker", "strategy"],
    ).reset_index(drop=True)

    return combined_comparison, combined_summary
