from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_PORTFOLIO_SUMMARY_COLUMNS = {
    "ticker",
    "total_return",
    "annualized_return",
    "sharpe_ratio",
    "max_drawdown",
}


def create_portfolio_strategy_ranking(
    portfolio_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Create a risk-adjusted ranking of portfolio strategies."""
    missing = REQUIRED_PORTFOLIO_SUMMARY_COLUMNS - set(portfolio_summary.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    ranking = portfolio_summary.copy()

    ranking["return_to_drawdown"] = np.where(
        ranking["max_drawdown"].abs() > 0,
        ranking["total_return"] / ranking["max_drawdown"].abs(),
        np.nan,
    )

    ranking = ranking.sort_values(
        ["sharpe_ratio", "return_to_drawdown", "max_drawdown"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    ranking.insert(0, "rank", range(1, len(ranking) + 1))

    preferred_columns = [
        "rank",
        "ticker",
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "return_to_drawdown",
        "average_asset_count",
        "average_volatility_scale",
        "average_realised_annual_volatility",
    ]

    existing_columns = [
        column for column in preferred_columns if column in ranking.columns
    ]

    remaining_columns = [
        column for column in ranking.columns if column not in existing_columns
    ]

    return ranking[existing_columns + remaining_columns]
