from __future__ import annotations

import pandas as pd

from quantlab.backtesting.sma import (
    SMABacktestConfig,
    run_sma_backtest,
    summarize_sma_backtest,
)


def run_sma_parameter_sweep(
    prices: pd.DataFrame,
    ticker: str,
    short_windows: list[int],
    long_windows: list[int],
    transaction_cost_bps: float = 5.0,
) -> pd.DataFrame:
    """Run SMA parameter sweep for one ticker."""
    summaries = []

    for short_window in short_windows:
        for long_window in long_windows:
            if short_window >= long_window:
                continue

            config = SMABacktestConfig(
                ticker=ticker,
                short_window=short_window,
                long_window=long_window,
                transaction_cost_bps=transaction_cost_bps,
            )

            results = run_sma_backtest(prices, config)
            summary = summarize_sma_backtest(results)

            summary["short_window"] = short_window
            summary["long_window"] = long_window
            summary["transaction_cost_bps"] = transaction_cost_bps

            summaries.append(summary)

    if not summaries:
        raise ValueError("No valid SMA parameter combinations were tested.")

    combined = pd.concat(summaries, ignore_index=True)

    return combined.sort_values(
        ["sharpe_ratio", "total_return"],
        ascending=[False, False],
    ).reset_index(drop=True)
