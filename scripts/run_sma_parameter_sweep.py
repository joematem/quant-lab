from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.backtesting.parameter_sweep import run_sma_parameter_sweep
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run SMA parameter sweep for one or more tickers.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


@app.command()
def main(
    tickers: TickersArg,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    short_windows = [5, 10, 20, 30, 50]
    long_windows = [50, 100, 150, 200]

    reports_dir = project_path("reports", "backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    for ticker in tickers:
        prices = query_prices(connection, ticker=ticker)

        sweep = run_sma_parameter_sweep(
            prices=prices,
            ticker=ticker,
            short_windows=short_windows,
            long_windows=long_windows,
            transaction_cost_bps=transaction_cost_bps,
        )

        output_path = reports_dir / f"sma_parameter_sweep_{ticker.upper()}.csv"
        sweep.to_csv(output_path, index=False)

        console.print(
            f"[bold green]SMA parameter sweep complete for {ticker.upper()}[/bold green]"
        )
        console.print(sweep.head(10))
        console.print(f"Saved sweep results: {output_path}")


if __name__ == "__main__":
    app()
