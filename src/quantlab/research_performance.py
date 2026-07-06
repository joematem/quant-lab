from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def calculate_cumulative_returns(
    returns: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate cumulative returns from daily returns."""
    clean_returns = returns.dropna(subset=["daily_return"]).copy()

    clean_returns["cumulative_return"] = clean_returns.groupby("ticker")[
        "daily_return"
    ].transform(lambda x: (1 + x).cumprod() - 1)

    return clean_returns


def calculate_drawdowns(
    returns: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate drawdowns from daily returns."""
    cumulative = calculate_cumulative_returns(returns)
    cumulative["wealth_index"] = 1 + cumulative["cumulative_return"]

    cumulative["previous_peak"] = cumulative.groupby("ticker")["wealth_index"].cummax()
    cumulative["drawdown"] = (
        cumulative["wealth_index"] / cumulative["previous_peak"]
    ) - 1

    return cumulative


def summarize_performance(
    returns: pd.DataFrame,
    risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    """Create ticker-level performance summary."""
    clean_returns = returns.dropna(subset=["daily_return"]).copy()

    summaries = []

    for ticker, group in clean_returns.groupby("ticker"):
        daily_returns = group["daily_return"]

        observations = len(daily_returns)
        total_return = (1 + daily_returns).prod() - 1

        annualized_return = (1 + total_return) ** (
            TRADING_DAYS_PER_YEAR / observations
        ) - 1

        annualized_volatility = daily_returns.std(ddof=1) * np.sqrt(
            TRADING_DAYS_PER_YEAR
        )

        excess_return = annualized_return - risk_free_rate
        sharpe_ratio = (
            excess_return / annualized_volatility
            if annualized_volatility != 0
            else np.nan
        )

        drawdowns = calculate_drawdowns(group)
        max_drawdown = drawdowns["drawdown"].min()

        summaries.append(
            {
                "ticker": ticker,
                "observations": observations,
                "total_return": total_return,
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "best_daily_return": daily_returns.max(),
                "worst_daily_return": daily_returns.min(),
            }
        )

    return pd.DataFrame(summaries).sort_values("ticker").reset_index(drop=True)
