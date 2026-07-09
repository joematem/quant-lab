from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.cost_stress import summarize_transaction_cost_stress
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run transaction cost stress tests.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

ShortOption = Annotated[int, typer.Option(help="Short moving average window")]
LongOption = Annotated[int, typer.Option(help="Long moving average window")]
CostsOption = Annotated[
    str,
    typer.Option(help="Comma-separated transaction costs in bps"),
]


def parse_costs(costs: str) -> list[float]:
    """Parse comma-separated transaction cost values."""
    parsed = [float(value.strip()) for value in costs.split(",") if value.strip()]

    if not parsed:
        raise ValueError("At least one transaction cost must be provided.")

    return parsed


@app.command()
def main(
    tickers: TickersArg,
    short_window: ShortOption = 20,
    long_window: LongOption = 50,
    costs_bps: CostsOption = "5,10,25,50",
) -> None:
    ticker_args = [ticker.upper() for ticker in tickers]
    reports_dir = project_path("reports", "backtests")

    all_summaries = []

    for cost_bps in parse_costs(costs_bps):
        console.rule(f"[bold blue]Testing transaction cost: {cost_bps} bps")

        subprocess.run(
            [
                sys.executable,
                "scripts/run_multi_ticker_sma_backtest.py",
                *ticker_args,
                "--short-window",
                str(short_window),
                "--long-window",
                str(long_window),
                "--transaction-cost-bps",
                str(cost_bps),
            ],
            check=True,
        )

        summary_path = reports_dir / "multi_ticker_sma_summary.csv"
        summary = pd.read_csv(summary_path)
        summary["transaction_cost_bps"] = cost_bps
        all_summaries.append(summary)

    combined = pd.concat(all_summaries, ignore_index=True)
    stress_summary = summarize_transaction_cost_stress(combined)

    output_path = reports_dir / "transaction_cost_stress_summary.csv"
    stress_summary.to_csv(output_path, index=False)

    console.print("[bold green]Transaction cost stress test complete[/bold green]")
    console.print(stress_summary)
    console.print(f"Saved stress summary: {output_path}")


if __name__ == "__main__":
    app()
