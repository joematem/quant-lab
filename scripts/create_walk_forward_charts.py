from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.walk_forward import (
    WalkForwardConfig,
    run_sma_walk_forward_validation,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path
from quantlab.visualization import plot_walk_forward_metric

app = typer.Typer(help="Create walk-forward validation charts.")
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

    figures_dir = project_path("reports", "backtests", "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    chart_specs = {
        "test_sharpe_ratio": figures_dir / "walk_forward_sharpe.png",
        "selected_short_window": figures_dir / "walk_forward_selected_short_window.png",
        "selected_long_window": figures_dir / "walk_forward_selected_long_window.png",
    }

    for metric, output_path in chart_specs.items():
        plot_walk_forward_metric(combined_results, metric, output_path)
        console.print(f"Saved {metric} chart: {output_path}")

    console.print("[bold green]Walk-forward charts complete[/bold green]")


if __name__ == "__main__":
    app()
