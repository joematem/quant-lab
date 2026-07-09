from __future__ import annotations

from pathlib import Path

import pandas as pd


def format_percentage(value: float) -> str:
    """Format decimal value as percentage."""
    return f"{value:.2%}"


def format_float(value: float) -> str:
    """Format float for reports."""
    return f"{value:.4f}"


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Convert a DataFrame to markdown without index."""
    return df.to_markdown(index=False)


def create_sma_research_report(
    walk_forward_summary: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Create a Markdown research report for the SMA strategy."""
    required_columns = {
        "ticker",
        "walk_forward_windows",
        "mean_test_total_return",
        "positive_return_rate",
        "mean_test_sharpe_ratio",
        "positive_sharpe_rate",
        "mean_test_max_drawdown",
        "worst_test_max_drawdown",
        "most_common_short_window",
        "most_common_long_window",
        "parameter_change_count",
    }

    missing = required_columns - set(walk_forward_summary.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = walk_forward_summary.copy()

    display_summary = summary[
        [
            "ticker",
            "walk_forward_windows",
            "mean_test_total_return",
            "positive_return_rate",
            "mean_test_sharpe_ratio",
            "positive_sharpe_rate",
            "mean_test_max_drawdown",
            "worst_test_max_drawdown",
            "most_common_short_window",
            "most_common_long_window",
            "parameter_change_count",
        ]
    ].copy()

    for column in [
        "mean_test_total_return",
        "positive_return_rate",
        "positive_sharpe_rate",
        "mean_test_max_drawdown",
        "worst_test_max_drawdown",
    ]:
        display_summary[column] = display_summary[column].map(format_percentage)

    display_summary["mean_test_sharpe_ratio"] = display_summary[
        "mean_test_sharpe_ratio"
    ].map(format_float)

    best_ticker = summary.iloc[0]["ticker"]

    report = f"""# SMA Crossover Strategy Research Report

## 1. Strategy overview

This report evaluates a simple long-only moving-average crossover strategy.

The strategy enters a long position when the short moving average is above the long moving average. 
Signals are shifted by one trading day to reduce look-ahead bias. Transaction costs are included.

## 2. Instruments tested

The strategy was tested on:

- AAPL
- MSFT
- NVDA

## 3. Research methodology

The workflow included:

1. Yahoo Finance daily OHLCV data ingestion.
2. Local Parquet storage.
3. DuckDB-based research querying.
4. SMA backtesting with transaction costs.
5. Buy-and-hold benchmark comparison.
6. Parameter sweep across SMA windows.
7. Walk-forward validation using rolling train/test periods.
8. Robustness summary across tickers.

## 4. Walk-forward robustness summary

{dataframe_to_markdown(display_summary)}

## 5. Main finding

Based on mean walk-forward Sharpe ratio, the strongest ticker in this test was **{best_ticker}**.

However, the parameter change counts show that the selected SMA windows are not perfectly stable across time. 
This suggests that the strategy may be sensitive to market regime changes.

## 6. Charts generated

The following charts were generated locally:

- `reports/backtests/figures/walk_forward_sharpe.png`
- `reports/backtests/figures/walk_forward_selected_short_window.png`
- `reports/backtests/figures/walk_forward_selected_long_window.png`
- `reports/backtests/figures/multi_ticker_sma_vs_buy_hold.png`

## 7. Limitations

This research is still preliminary.

Important limitations:

- Yahoo Finance data may contain adjustments and inconsistencies.
- Only three large-cap technology stocks were tested.
- The strategy is long-only.
- No liquidity model beyond simple transaction costs is included.
- No volatility targeting is included.
- No portfolio construction layer is included.
- No live execution layer is included.
- No statistical significance testing is included yet.
- No survivorship-bias-free universe is used.

## 8. Next research steps

Recommended next steps:

1. Add volatility targeting.
2. Add benchmark-relative metrics.
3. Add Monte Carlo robustness testing.
4. Add train/test equity curve charts.
5. Add portfolio-level backtesting.
6. Add risk limits.
7. Add experiment configuration files.
8. Add reproducible report generation from one command.

## 9. Research conclusion

The SMA crossover strategy shows some positive walk-forward evidence, especially for the strongest-ranked ticker. 
However, the evidence is not sufficient for live deployment.

The correct conclusion is: continue research, improve robustness testing, and avoid live trading until the system includes stronger risk controls and broader validation.
"""

    output_path.write_text(report)

    return output_path
