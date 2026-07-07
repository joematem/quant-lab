from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.backtesting.sma import (
    SMABacktestConfig,
    run_sma_backtest,
    summarize_sma_backtest,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run an SMA crossover backtest.")
console = Console()

TickerArg = Annotated[str, typer.Argument(help="Ticker symbol, e.g. AAPL")]
ShortOption = Annotated[int, typer.Option(help="Short moving average window")]
LongOption = Annotated[int, typer.Option(help="Long moving average window")]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


@app.command()
def main(
    ticker: TickerArg,
    short_window: ShortOption = 20,
    long_window: LongOption = 50,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    prices = query_prices(connection, ticker=ticker)

    config = SMABacktestConfig(
        ticker=ticker,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
    )

    results = run_sma_backtest(prices, config)
    summary = summarize_sma_backtest(results)

    reports_dir = project_path("reports", "backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    result_path = reports_dir / f"{ticker.upper()}_sma_backtest.csv"
    summary_path = reports_dir / f"{ticker.upper()}_sma_summary.csv"

    results.to_csv(result_path, index=False)
    summary.to_csv(summary_path, index=False)

    console.print("[bold green]SMA backtest complete[/bold green]")
    console.print(summary)
    console.print(f"Saved detailed backtest: {result_path}")
    console.print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    app()
