from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def _max_drawdown_from_returns(daily_returns: np.ndarray) -> float:
    equity = np.cumprod(1.0 + daily_returns)
    running_max = np.maximum.accumulate(equity)
    drawdown = equity / running_max - 1.0

    return float(drawdown.min())


def run_return_bootstrap_monte_carlo(
    returns: pd.DataFrame,
    simulations: int,
    seed: int,
    output_ticker: str,
) -> pd.DataFrame:
    """Run bootstrap Monte Carlo simulation on daily returns."""
    required_columns = {"ticker", "date", "daily_return"}
    missing = required_columns - set(returns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if simulations <= 0:
        raise ValueError("simulations must be positive.")

    df = returns.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    daily_returns = df["daily_return"].dropna().to_numpy()

    if len(daily_returns) < 2:
        raise ValueError("At least two daily returns are required.")

    rng = np.random.default_rng(seed)
    observations = len(daily_returns)

    rows = []

    for simulation_id in range(1, simulations + 1):
        sampled_returns = rng.choice(
            daily_returns,
            size=observations,
            replace=True,
        )

        total_return = float(np.prod(1.0 + sampled_returns) - 1.0)
        annualized_return = float(
            (1.0 + total_return) ** (TRADING_DAYS_PER_YEAR / observations) - 1.0
        )
        annualized_volatility = float(
            np.std(sampled_returns, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
        )

        if annualized_volatility == 0:
            sharpe_ratio = np.nan
        else:
            sharpe_ratio = annualized_return / annualized_volatility

        rows.append(
            {
                "ticker": output_ticker,
                "simulation_id": simulation_id,
                "observations": observations,
                "total_return": total_return,
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": _max_drawdown_from_returns(sampled_returns),
            }
        )

    return pd.DataFrame(rows)


def summarize_monte_carlo_results(
    monte_carlo_results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize Monte Carlo robustness results."""
    required_columns = {
        "ticker",
        "simulation_id",
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
    }

    missing = required_columns - set(monte_carlo_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rows = []

    for ticker, group in monte_carlo_results.groupby("ticker"):
        rows.append(
            {
                "ticker": ticker,
                "simulations": len(group),
                "total_return_p05": group["total_return"].quantile(0.05),
                "total_return_p50": group["total_return"].quantile(0.50),
                "total_return_p95": group["total_return"].quantile(0.95),
                "sharpe_ratio_p05": group["sharpe_ratio"].quantile(0.05),
                "sharpe_ratio_p50": group["sharpe_ratio"].quantile(0.50),
                "sharpe_ratio_p95": group["sharpe_ratio"].quantile(0.95),
                "max_drawdown_p05": group["max_drawdown"].quantile(0.05),
                "max_drawdown_p50": group["max_drawdown"].quantile(0.50),
                "max_drawdown_p95": group["max_drawdown"].quantile(0.95),
                "probability_positive_return": (group["total_return"] > 0).mean(),
                "probability_negative_return": (group["total_return"] < 0).mean(),
                "probability_drawdown_worse_than_30pct": (
                    group["max_drawdown"] < -0.30
                ).mean(),
            }
        )

    return pd.DataFrame(rows)
