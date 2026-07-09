from __future__ import annotations

import pandas as pd

from quantlab.research_performance import summarize_performance


def build_equal_weight_portfolio_returns(
    backtest_results: pd.DataFrame,
    return_column: str,
    portfolio_name: str,
) -> pd.DataFrame:
    """Build equal-weight portfolio returns from multi-ticker returns."""
    required_columns = {"ticker", "date", return_column}
    missing = required_columns - set(backtest_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = backtest_results.copy()
    df["date"] = pd.to_datetime(df["date"])

    returns = df.pivot_table(
        index="date",
        columns="ticker",
        values=return_column,
        aggfunc="mean",
    ).sort_index()

    portfolio_returns = returns.mean(axis=1, skipna=True).fillna(0.0)
    asset_count = returns.notna().sum(axis=1)

    portfolio = pd.DataFrame(
        {
            "ticker": portfolio_name,
            "date": portfolio_returns.index,
            "daily_return": portfolio_returns.values,
            "asset_count": asset_count.values,
        }
    )

    portfolio["adj_close"] = 100.0 * (1.0 + portfolio["daily_return"]).cumprod()

    return portfolio.reset_index(drop=True)


def summarize_equal_weight_portfolio(
    portfolio_returns: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize equal-weight portfolio performance."""
    required_columns = {"ticker", "date", "adj_close", "daily_return"}
    missing = required_columns - set(portfolio_returns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    summary = summarize_performance(portfolio_returns)

    if "asset_count" in portfolio_returns.columns:
        summary["average_asset_count"] = portfolio_returns["asset_count"].mean()

    return summary
