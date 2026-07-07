from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.backtesting.multi_ticker_benchmark import (
    compare_multi_ticker_sma_to_buy_and_hold,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path
from quantlab.visualization import plot_multi_ticker_strategy_comparison

app = typer.Typer(help="Create multi-ticker SMA versus buy-and-hold chart.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

ShortOption = Annotated[int, typer.Option(help="Short moving average window")]
LongOption = Annotated[int, typer.Option(help="Long moving average window")]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


@app.command()
def main(
    tickers: TickersArg,
    short_window: ShortOption = 20,
    long_window: LongOption = 50,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    prices_by_ticker = {
        ticker.upper(): query_prices(connection, ticker=ticker) for ticker in tickers
    }

    comparison, _summary = compare_multi_ticker_sma_to_buy_and_hold(
        prices_by_ticker=prices_by_ticker,
        short_window=short_window,
        long_window=long_window,
        transaction_cost_bps=transaction_cost_bps,
    )

    figures_dir = project_path("reports", "backtests", "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    chart_path = figures_dir / "multi_ticker_sma_vs_buy_hold.png"

    plot_multi_ticker_strategy_comparison(comparison, chart_path)

    console.print("[bold green]Multi-ticker benchmark chart complete[/bold green]")
    console.print(f"Saved chart: {chart_path}")


if __name__ == "__main__":
    app()
