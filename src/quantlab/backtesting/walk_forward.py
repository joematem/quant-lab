from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quantlab.backtesting.parameter_sweep import run_sma_parameter_sweep
from quantlab.backtesting.sma import SMABacktestConfig, run_sma_backtest
from quantlab.research_performance import summarize_performance


@dataclass(frozen=True)
class WalkForwardConfig:
    ticker: str
    train_years: int = 3
    test_years: int = 1
    short_windows: tuple[int, ...] = (5, 10, 20, 30, 50)
    long_windows: tuple[int, ...] = (50, 100, 150, 200)
    transaction_cost_bps: float = 5.0


def _prepare_walk_forward_prices(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
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


def run_sma_walk_forward_validation(
    prices: pd.DataFrame,
    config: WalkForwardConfig,
) -> pd.DataFrame:
    """Run walk-forward validation for SMA crossover strategy."""
    df = _prepare_walk_forward_prices(prices, config.ticker)

    start_year = int(df["date"].dt.year.min())
    end_year = int(df["date"].dt.year.max())

    rows = []

    first_train_start = start_year
    last_possible_test_end = end_year

    current_train_start = first_train_start

    while True:
        train_start_year = current_train_start
        train_end_year = train_start_year + config.train_years - 1
        test_start_year = train_end_year + 1
        test_end_year = test_start_year + config.test_years - 1

        if test_end_year > last_possible_test_end:
            break

        train_data = df[
            (df["date"].dt.year >= train_start_year)
            & (df["date"].dt.year <= train_end_year)
        ].copy()

        test_data = df[
            (df["date"].dt.year >= test_start_year)
            & (df["date"].dt.year <= test_end_year)
        ].copy()

        if train_data.empty or test_data.empty:
            current_train_start += config.test_years
            continue

        sweep = run_sma_parameter_sweep(
            prices=train_data,
            ticker=config.ticker,
            short_windows=list(config.short_windows),
            long_windows=list(config.long_windows),
            transaction_cost_bps=config.transaction_cost_bps,
        )

        best = sweep.iloc[0]
        best_short_window = int(best["short_window"])
        best_long_window = int(best["long_window"])

        backtest_config = SMABacktestConfig(
            ticker=config.ticker,
            short_window=best_short_window,
            long_window=best_long_window,
            transaction_cost_bps=config.transaction_cost_bps,
        )

        test_results = run_sma_backtest(test_data, backtest_config)

        performance_input = test_results[
            ["ticker", "date", "adj_close", "strategy_net_return"]
        ].rename(columns={"strategy_net_return": "daily_return"})

        test_summary = summarize_performance(performance_input).iloc[0]

        rows.append(
            {
                "ticker": config.ticker.upper(),
                "train_start_year": train_start_year,
                "train_end_year": train_end_year,
                "test_start_year": test_start_year,
                "test_end_year": test_end_year,
                "selected_short_window": best_short_window,
                "selected_long_window": best_long_window,
                "train_sharpe_ratio": float(best["sharpe_ratio"]),
                "test_total_return": float(test_summary["total_return"]),
                "test_annualized_return": float(test_summary["annualized_return"]),
                "test_annualized_volatility": float(
                    test_summary["annualized_volatility"]
                ),
                "test_sharpe_ratio": float(test_summary["sharpe_ratio"]),
                "test_max_drawdown": float(test_summary["max_drawdown"]),
            }
        )

        current_train_start += config.test_years

    if not rows:
        raise ValueError("No walk-forward windows could be created.")

    return pd.DataFrame(rows)
