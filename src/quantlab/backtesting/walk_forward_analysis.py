from __future__ import annotations

import pandas as pd

REQUIRED_WALK_FORWARD_COLUMNS = {
    "ticker",
    "train_start_year",
    "train_end_year",
    "test_start_year",
    "test_end_year",
    "selected_short_window",
    "selected_long_window",
    "test_total_return",
    "test_sharpe_ratio",
    "test_max_drawdown",
}


def summarize_walk_forward_results(
    walk_forward_results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize walk-forward validation results by ticker."""
    missing = REQUIRED_WALK_FORWARD_COLUMNS - set(walk_forward_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    summaries = []

    for ticker, group in walk_forward_results.groupby("ticker"):
        ordered = group.sort_values("test_start_year").copy()

        valid_sharpe = ordered["test_sharpe_ratio"].dropna()
        positive_sharpe_rate = (
            float((valid_sharpe > 0).mean()) if not valid_sharpe.empty else 0.0
        )

        parameter_pairs = list(
            zip(
                ordered["selected_short_window"],
                ordered["selected_long_window"],
                strict=False,
            )
        )

        parameter_change_count = sum(
            current != previous
            for previous, current in zip(
                parameter_pairs,
                parameter_pairs[1:],
                strict=False,
            )
        )

        most_common_short_window = int(ordered["selected_short_window"].mode().iloc[0])
        most_common_long_window = int(ordered["selected_long_window"].mode().iloc[0])

        summaries.append(
            {
                "ticker": ticker,
                "walk_forward_windows": len(ordered),
                "mean_test_total_return": ordered["test_total_return"].mean(),
                "median_test_total_return": ordered["test_total_return"].median(),
                "positive_return_rate": (ordered["test_total_return"] > 0).mean(),
                "mean_test_sharpe_ratio": valid_sharpe.mean(),
                "median_test_sharpe_ratio": valid_sharpe.median(),
                "positive_sharpe_rate": positive_sharpe_rate,
                "mean_test_max_drawdown": ordered["test_max_drawdown"].mean(),
                "worst_test_max_drawdown": ordered["test_max_drawdown"].min(),
                "most_common_short_window": most_common_short_window,
                "most_common_long_window": most_common_long_window,
                "parameter_change_count": parameter_change_count,
            }
        )

    return (
        pd.DataFrame(summaries)
        .sort_values(
            ["mean_test_sharpe_ratio", "positive_return_rate"],
            ascending=[False, False],
        )
        .reset_index(drop=True)
    )
