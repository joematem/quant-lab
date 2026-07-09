from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer(help="Run the full SMA research experiment.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

StartOption = Annotated[str, typer.Option(help="Yahoo Finance start date")]
ShortOption = Annotated[int, typer.Option(help="Short moving average window")]
LongOption = Annotated[int, typer.Option(help="Long moving average window")]
TrainYearsOption = Annotated[int, typer.Option(help="Training window in years")]
TestYearsOption = Annotated[int, typer.Option(help="Testing window in years")]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]


def run_step(description: str, command: list[str]) -> None:
    """Run one experiment step."""
    console.rule(f"[bold blue]{description}")

    subprocess.run(
        [sys.executable, *command],
        check=True,
    )


@app.command()
def main(
    tickers: TickersArg,
    start: StartOption = "2015-01-01",
    short_window: ShortOption = 20,
    long_window: LongOption = 50,
    train_years: TrainYearsOption = 3,
    test_years: TestYearsOption = 1,
    transaction_cost_bps: CostOption = 5.0,
) -> None:
    ticker_args = [ticker.upper() for ticker in tickers]

    run_step(
        "Downloading Yahoo Finance data",
        [
            "scripts/download_yahoo_prices.py",
            *ticker_args,
            "--start",
            start,
        ],
    )

    run_step(
        "Creating DuckDB research outputs",
        ["scripts/query_yahoo_duckdb.py"],
    )

    run_step(
        "Creating performance report",
        ["scripts/create_performance_report.py"],
    )

    run_step(
        "Creating performance charts",
        ["scripts/create_performance_charts.py"],
    )

    run_step(
        "Running multi-ticker SMA backtest",
        [
            "scripts/run_multi_ticker_sma_backtest.py",
            *ticker_args,
            "--short-window",
            str(short_window),
            "--long-window",
            str(long_window),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Comparing SMA to buy-and-hold",
        [
            "scripts/compare_multi_ticker_sma_to_buy_hold.py",
            *ticker_args,
            "--short-window",
            str(short_window),
            "--long-window",
            str(long_window),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Creating multi-ticker benchmark chart",
        [
            "scripts/create_multi_ticker_benchmark_chart.py",
            *ticker_args,
            "--short-window",
            str(short_window),
            "--long-window",
            str(long_window),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Running SMA parameter sweep",
        [
            "scripts/run_sma_parameter_sweep.py",
            *ticker_args,
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Running walk-forward validation",
        [
            "scripts/run_sma_walk_forward.py",
            *ticker_args,
            "--train-years",
            str(train_years),
            "--test-years",
            str(test_years),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Creating walk-forward summary",
        [
            "scripts/create_walk_forward_summary.py",
            *ticker_args,
            "--train-years",
            str(train_years),
            "--test-years",
            str(test_years),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Creating walk-forward charts",
        [
            "scripts/create_walk_forward_charts.py",
            *ticker_args,
            "--train-years",
            str(train_years),
            "--test-years",
            str(test_years),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    run_step(
        "Creating SMA research report",
        [
            "scripts/create_sma_research_report.py",
            *ticker_args,
            "--train-years",
            str(train_years),
            "--test-years",
            str(test_years),
            "--transaction-cost-bps",
            str(transaction_cost_bps),
        ],
    )

    console.rule("[bold green]Full SMA research experiment complete")


if __name__ == "__main__":
    app()
