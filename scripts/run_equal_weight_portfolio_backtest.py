from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.portfolio import (
    build_equal_weight_portfolio_returns,
    summarize_equal_weight_portfolio,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run equal-weight portfolio backtest from SMA results.")
console = Console()


def detect_buy_hold_return_column(backtest_results: pd.DataFrame) -> str:
    """Detect the raw asset return column for buy-and-hold comparison."""
    candidates = [
        "daily_return",
        "asset_return",
        "price_return",
        "simple_return",
        "return",
    ]

    for candidate in candidates:
        if candidate in backtest_results.columns:
            return candidate

    available = ", ".join(backtest_results.columns)
    raise ValueError(
        "Could not detect buy-and-hold return column. "
        f"Available columns: {available}"
    )


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")
    input_path = reports_dir / "multi_ticker_sma_results.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing multi-ticker SMA results. Run `make experiment` first."
        )

    backtest_results = pd.read_csv(input_path)

    buy_hold_return_column = detect_buy_hold_return_column(backtest_results)

    sma_portfolio = build_equal_weight_portfolio_returns(
        backtest_results=backtest_results,
        return_column="strategy_net_return",
        portfolio_name="equal_weight_sma",
    )

    buy_hold_portfolio = build_equal_weight_portfolio_returns(
        backtest_results=backtest_results,
        return_column=buy_hold_return_column,
        portfolio_name="equal_weight_buy_hold",
    )

    combined_returns = pd.concat(
        [sma_portfolio, buy_hold_portfolio],
        ignore_index=True,
    )

    summary = summarize_equal_weight_portfolio(combined_returns)

    returns_path = reports_dir / "portfolio_equal_weight_returns.csv"
    summary_path = reports_dir / "portfolio_equal_weight_summary.csv"

    combined_returns.to_csv(returns_path, index=False)
    summary.to_csv(summary_path, index=False)

    console.print("[bold green]Equal-weight portfolio backtest complete[/bold green]")
    console.print(f"Buy-and-hold return column: {buy_hold_return_column}")
    console.print(summary)
    console.print(f"Saved portfolio returns: {returns_path}")
    console.print(f"Saved portfolio summary: {summary_path}")


if __name__ == "__main__":
    app()
