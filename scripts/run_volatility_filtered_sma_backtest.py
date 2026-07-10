from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.volatility_filtered_sma import (
    VolatilityFilteredSMAConfig,
    run_volatility_filtered_sma_backtest,
    summarize_volatility_filtered_sma_backtest,
)
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run volatility-filtered SMA backtests.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

ShortOption = Annotated[int, typer.Option(help="Short moving average window")]
LongOption = Annotated[int, typer.Option(help="Long moving average window")]
VolLookbackOption = Annotated[int, typer.Option(help="Volatility lookback window")]
MaxVolOption = Annotated[
    float,
    typer.Option(help="Maximum annualized volatility allowed for exposure"),
]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


@app.command()
def main(
    tickers: TickersArg,
    short_window: ShortOption = 20,
    long_window: LongOption = 50,
    volatility_lookback: VolLookbackOption = 63,
    max_annualized_volatility: MaxVolOption = 0.40,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    all_results = []
    all_summaries = []

    for ticker in tickers:
        ticker_symbol = ticker.upper()
        prices = query_prices(connection, ticker=ticker_symbol)

        config = VolatilityFilteredSMAConfig(
            ticker=ticker_symbol,
            short_window=short_window,
            long_window=long_window,
            volatility_lookback=volatility_lookback,
            max_annualized_volatility=max_annualized_volatility,
            transaction_cost_bps=transaction_cost_bps,
        )

        results = run_volatility_filtered_sma_backtest(prices, config)
        summary = summarize_volatility_filtered_sma_backtest(results)

        all_results.append(results)
        all_summaries.append(summary)

    combined_results = pd.concat(all_results, ignore_index=True)
    combined_summary = pd.concat(all_summaries, ignore_index=True)

    reports_dir = project_path("reports", "backtests")
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_path = reports_dir / "volatility_filtered_sma_results.csv"
    summary_path = reports_dir / "volatility_filtered_sma_summary.csv"

    combined_results.to_csv(results_path, index=False)
    combined_summary.to_csv(summary_path, index=False)

    console.print("[bold green]Volatility-filtered SMA backtest complete[/bold green]")
    console.print(combined_summary)
    console.print(f"Saved results: {results_path}")
    console.print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    app()
