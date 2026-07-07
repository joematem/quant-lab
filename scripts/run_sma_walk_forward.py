from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.backtesting.walk_forward import (
    WalkForwardConfig,
    run_sma_walk_forward_validation,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run SMA walk-forward validation.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

TrainYearsOption = Annotated[int, typer.Option(help="Training window in years")]
TestYearsOption = Annotated[int, typer.Option(help="Testing window in years")]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


@app.command()
def main(
    tickers: TickersArg,
    train_years: TrainYearsOption = 3,
    test_years: TestYearsOption = 1,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    reports_dir = project_path("reports", "backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    for ticker in tickers:
        prices = query_prices(connection, ticker=ticker)

        config = WalkForwardConfig(
            ticker=ticker,
            train_years=train_years,
            test_years=test_years,
            transaction_cost_bps=transaction_cost_bps,
        )

        result = run_sma_walk_forward_validation(prices, config)

        output_path = reports_dir / f"walk_forward_{ticker.upper()}.csv"
        result.to_csv(output_path, index=False)

        console.print(
            "[bold green]"
            f"SMA walk-forward validation complete for {ticker.upper()}"
            "[/bold green]"
        )
        console.print(result)
        console.print(f"Saved walk-forward results: {output_path}")


if __name__ == "__main__":
    app()
