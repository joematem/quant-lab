from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quantlab.backtesting.sma import (
    generate_sma_signals,
    prepare_price_data,
    summarize_sma_backtest,
)

TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class VolatilityFilteredSMAConfig:
    ticker: str
    short_window: int = 20
    long_window: int = 50
    volatility_lookback: int = 63
    max_annualized_volatility: float = 0.40
    transaction_cost_bps: float = 5.0


def add_realized_volatility(
    prices: pd.DataFrame,
    lookback: int,
) -> pd.DataFrame:
    """Add realised annualised volatility to price data."""
    if lookback <= 1:
        raise ValueError("lookback must be greater than 1")

    required_columns = {"adj_close"}
    missing = required_columns - set(prices.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = prices.copy()
    df["asset_return"] = df["adj_close"].pct_change()
    df["realized_annualized_volatility"] = df["asset_return"].rolling(
        window=lookback
    ).std() * (TRADING_DAYS_PER_YEAR**0.5)

    return df


def generate_volatility_filtered_sma_signals(
    prices: pd.DataFrame,
    short_window: int,
    long_window: int,
    volatility_lookback: int,
    max_annualized_volatility: float,
) -> pd.DataFrame:
    """Generate SMA signals filtered by realised volatility."""
    if max_annualized_volatility <= 0:
        raise ValueError("max_annualized_volatility must be positive")

    df = generate_sma_signals(
        prices,
        short_window=short_window,
        long_window=long_window,
    )
    df = add_realized_volatility(df, lookback=volatility_lookback)

    df["volatility_filter"] = (
        df["realized_annualized_volatility"] <= max_annualized_volatility
    ).astype(float)

    df["filtered_signal"] = df["signal"] * df["volatility_filter"]

    # Shift filtered position to avoid look-ahead bias.
    df["position"] = df["filtered_signal"].shift(1).fillna(0.0)

    return df


def run_volatility_filtered_sma_backtest(
    prices: pd.DataFrame,
    config: VolatilityFilteredSMAConfig,
) -> pd.DataFrame:
    """Run volatility-filtered SMA backtest with transaction costs."""
    df = prepare_price_data(prices, config.ticker)

    df = generate_volatility_filtered_sma_signals(
        df,
        short_window=config.short_window,
        long_window=config.long_window,
        volatility_lookback=config.volatility_lookback,
        max_annualized_volatility=config.max_annualized_volatility,
    )

    df["asset_return"] = df["adj_close"].pct_change()
    df["trade"] = df["position"].diff().abs().fillna(df["position"].abs())

    transaction_cost_rate = config.transaction_cost_bps / 10_000
    df["strategy_gross_return"] = df["position"] * df["asset_return"]
    df["transaction_cost"] = df["trade"] * transaction_cost_rate
    df["strategy_net_return"] = df["strategy_gross_return"] - df["transaction_cost"]

    df["strategy_net_return"] = df["strategy_net_return"].fillna(0.0)
    df["cumulative_return"] = (1 + df["strategy_net_return"]).cumprod() - 1
    df["ticker"] = config.ticker.upper()

    return df


def summarize_volatility_filtered_sma_backtest(
    backtest_results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize volatility-filtered SMA backtest."""
    summary = summarize_sma_backtest(backtest_results)

    summary["average_volatility_filter"] = float(
        backtest_results["volatility_filter"].mean()
    )
    summary["average_realized_annualized_volatility"] = float(
        backtest_results["realized_annualized_volatility"].mean()
    )

    return summary
