from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.research_performance import summarize_performance

TRADING_DAYS_PER_YEAR = 252


def apply_volatility_target(
    returns: pd.DataFrame,
    target_annual_volatility: float,
    lookback_days: int,
    max_leverage: float,
    output_ticker: str,
) -> pd.DataFrame:
    """Apply volatility targeting to a return series."""
    required_columns = {"ticker", "date", "daily_return"}
    missing = required_columns - set(returns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if target_annual_volatility <= 0:
        raise ValueError("target_annual_volatility must be positive.")

    if lookback_days <= 1:
        raise ValueError("lookback_days must be greater than 1.")

    if max_leverage <= 0:
        raise ValueError("max_leverage must be positive.")

    df = returns.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    realised_volatility = df["daily_return"].rolling(lookback_days).std().shift(
        1
    ) * np.sqrt(TRADING_DAYS_PER_YEAR)

    volatility_scale = target_annual_volatility / realised_volatility
    volatility_scale = volatility_scale.replace([np.inf, -np.inf], np.nan)
    volatility_scale = volatility_scale.clip(lower=0.0, upper=max_leverage)
    volatility_scale = volatility_scale.fillna(0.0)

    targeted_return = df["daily_return"] * volatility_scale

    result = pd.DataFrame(
        {
            "ticker": output_ticker,
            "date": df["date"],
            "daily_return": targeted_return,
            "volatility_scale": volatility_scale,
            "realised_annual_volatility": realised_volatility,
            "target_annual_volatility": target_annual_volatility,
        }
    )

    result["adj_close"] = 100.0 * (1.0 + result["daily_return"]).cumprod()

    return result


def summarize_volatility_targeted_returns(
    targeted_returns: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize volatility-targeted return series."""
    required_columns = {"ticker", "date", "adj_close", "daily_return"}
    missing = required_columns - set(targeted_returns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    summary = summarize_performance(targeted_returns)

    if "volatility_scale" in targeted_returns.columns:
        summary["average_volatility_scale"] = targeted_returns[
            "volatility_scale"
        ].mean()

    if "realised_annual_volatility" in targeted_returns.columns:
        summary["average_realised_annual_volatility"] = targeted_returns[
            "realised_annual_volatility"
        ].mean()

    return summary
