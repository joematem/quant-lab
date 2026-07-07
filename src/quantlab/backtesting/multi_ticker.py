from __future__ import annotations

import pandas as pd

from quantlab.backtesting.sma import (
    SMABacktestConfig,
    run_sma_backtest,
    summarize_sma_backtest,
)


def run_multi_ticker_sma_backtest(
    prices_by_ticker: dict[str, pd.DataFrame],
    short_window: int = 20,
    long_window: int = 50,
    transaction_cost_bps: float = 5.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run SMA backtests across multiple tickers."""
    all_results = []
    all_summaries = []

    for ticker, prices in prices_by_ticker.items():
        config = SMABacktestConfig(
            ticker=ticker,
            short_window=short_window,
            long_window=long_window,
            transaction_cost_bps=transaction_cost_bps,
        )

        results = run_sma_backtest(prices, config)
        summary = summarize_sma_backtest(results)

        all_results.append(results)
        all_summaries.append(summary)

    combined_results = pd.concat(all_results, ignore_index=True)
    combined_summary = pd.concat(all_summaries, ignore_index=True)

    combined_summary = combined_summary.sort_values(
        "sharpe_ratio",
        ascending=False,
    ).reset_index(drop=True)

    return combined_results, combined_summary
