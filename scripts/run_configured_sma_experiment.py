from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console

from quantlab.config import load_sma_experiment_config

app = typer.Typer(help="Run SMA experiment from a YAML config file.")
console = Console()

ConfigArg = Annotated[
    str,
    typer.Argument(help="Path to YAML config file"),
]


@app.command()
def main(config_path: ConfigArg) -> None:
    config = load_sma_experiment_config(config_path)

    command = [
        "scripts/run_full_sma_research_experiment.py",
        *config.tickers,
        "--start",
        config.start,
        "--short-window",
        str(config.short_window),
        "--long-window",
        str(config.long_window),
        "--train-years",
        str(config.train_years),
        "--test-years",
        str(config.test_years),
        "--transaction-cost-bps",
        str(config.transaction_cost_bps),
    ]

    console.print("[bold green]Running configured SMA experiment[/bold green]")
    console.print(f"Config: {config_path}")
    console.print(f"Tickers: {', '.join(config.tickers)}")

    subprocess.run(
        [sys.executable, *command],
        check=True,
    )


if __name__ == "__main__":
    app()
