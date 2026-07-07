from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quantlab.research_performance import summarize_performance


@dataclass(frozen=True)
class SMABacktestConfig:
    ticker: str
    short_window: int = 20
    long_window: int = 50
    transaction_cost_bps: float = 5.0


def prepare_price_data(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Prepare ticker price data for backtesting."""
    required_columns = {"ticker", "date", "adj_close"}
    missing = required_columns - set(prices.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = prices.loc[prices["ticker"] == ticker.upper()].copy()
    if df.empty:
        raise ValueError(f"No price data found for ticker: {ticker}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


def generate_sma_signals(
    prices: pd.DataFrame,
    short_window: int,
    long_window: int,
) -> pd.DataFrame:
    """Generate SMA crossover signals."""
    if short_window >= long_window:
        raise ValueError("short_window must be less than long_window")

    df = prices.copy()

    df["short_sma"] = df["adj_close"].rolling(window=short_window).mean()
    df["long_sma"] = df["adj_close"].rolling(window=long_window).mean()

    df["signal"] = 0.0
    df.loc[df["short_sma"] > df["long_sma"], "signal"] = 1.0

    # Position is shifted by one day to avoid look-ahead bias.
    df["position"] = df["signal"].shift(1).fillna(0.0)

    return df


def run_sma_backtest(
    prices: pd.DataFrame,
    config: SMABacktestConfig,
) -> pd.DataFrame:
    """Run an SMA crossover backtest with transaction costs."""
    df = prepare_price_data(prices, config.ticker)
    df = generate_sma_signals(
        df,
        short_window=config.short_window,
        long_window=config.long_window,
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


def summarize_sma_backtest(backtest_results: pd.DataFrame) -> pd.DataFrame:
    """Create a summary table for the SMA backtest."""
    required_columns = {
        "ticker",
        "date",
        "adj_close",
        "strategy_net_return",
        "trade",
        "position",
    }
    missing = required_columns - set(backtest_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    performance_input = backtest_results[
        ["ticker", "date", "adj_close", "strategy_net_return"]
    ].rename(columns={"strategy_net_return": "daily_return"})

    summary = summarize_performance(performance_input)

    trade_count = int(backtest_results["trade"].sum())
    avg_exposure = float(backtest_results["position"].mean())

    summary["trade_count"] = trade_count
    summary["average_exposure"] = avg_exposure

    return summary
