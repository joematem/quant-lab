from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.backtesting.benchmark import compare_strategy_to_buy_and_hold
from quantlab.backtesting.sma import SMABacktestConfig, run_sma_backtest
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path
from quantlab.visualization import plot_strategy_comparison

app = typer.Typer(help="Create SMA versus buy-and-hold benchmark chart.")
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

    backtest_results = run_sma_backtest(prices, config)
    comparison = compare_strategy_to_buy_and_hold(backtest_results)

    figures_dir = project_path("reports", "backtests", "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    chart_path = figures_dir / f"{ticker.upper()}_sma_vs_buy_hold.png"

    plot_strategy_comparison(comparison, chart_path)

    console.print("[bold green]Benchmark comparison chart complete[/bold green]")
    console.print(f"Saved chart: {chart_path}")


if __name__ == "__main__":
    app()
