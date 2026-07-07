from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.walk_forward import (
    WalkForwardConfig,
    run_sma_walk_forward_validation,
)
from quantlab.backtesting.walk_forward_analysis import (
    summarize_walk_forward_results,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create walk-forward robustness summary.")
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

    all_results = []

    for ticker in tickers:
        prices = query_prices(connection, ticker=ticker)

        config = WalkForwardConfig(
            ticker=ticker,
            train_years=train_years,
            test_years=test_years,
            transaction_cost_bps=transaction_cost_bps,
        )

        result = run_sma_walk_forward_validation(prices, config)
        all_results.append(result)

    combined_results = pd.concat(all_results, ignore_index=True)
    summary = summarize_walk_forward_results(combined_results)

    reports_dir = project_path("reports", "backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    combined_path = reports_dir / "walk_forward_combined.csv"
    summary_path = reports_dir / "walk_forward_summary.csv"

    combined_results.to_csv(combined_path, index=False)
    summary.to_csv(summary_path, index=False)

    console.print("[bold green]Walk-forward robustness summary complete[/bold green]")
    console.print(summary)
    console.print(f"Saved combined results: {combined_path}")
    console.print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    app()
