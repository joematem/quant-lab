from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.walk_forward import (
    WalkForwardConfig,
    run_sma_walk_forward_validation,
)
from quantlab.backtesting.walk_forward_analysis import summarize_walk_forward_results
from quantlab.data.duckdb_prices import connect_duckdb, load_yahoo_prices, query_prices
from quantlab.reporting import create_sma_research_report
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create SMA strategy research report.")
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

    portfolio_summary_path = reports_dir / "portfolio_equal_weight_summary.csv"
    targeted_summary_path = reports_dir / "portfolio_volatility_targeted_summary.csv"
    portfolio_summaries = []

    if portfolio_summary_path.exists():
        portfolio_summaries.append(pd.read_csv(portfolio_summary_path))

    if targeted_summary_path.exists():
        portfolio_summaries.append(pd.read_csv(targeted_summary_path))

    portfolio_summary = None
    if portfolio_summaries:
        portfolio_summary = pd.concat(portfolio_summaries, ignore_index=True)

    ranking_path = reports_dir / "portfolio_strategy_comparison_summary.csv"
    portfolio_strategy_ranking = None

    if ranking_path.exists():
        portfolio_strategy_ranking = pd.read_csv(ranking_path)

    report_path = reports_dir / "sma_research_report.md"
    create_sma_research_report(
        walk_forward_summary=summary,
        output_path=report_path,
        portfolio_summary=portfolio_summary,
        portfolio_strategy_ranking=portfolio_strategy_ranking,
    )

    console.print("[bold green]SMA research report complete[/bold green]")
    console.print(f"Saved report: {report_path}")


if __name__ == "__main__":
    app()
