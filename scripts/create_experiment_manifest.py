from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.experiment_manifest import (
    build_experiment_manifest,
    default_sma_manifest_outputs,
    write_experiment_manifest,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create experiment reproducibility manifest.")
console = Console()

TickersOption = Annotated[
    str,
    typer.Option(help="Comma-separated ticker universe"),
]
ShortWindowOption = Annotated[int, typer.Option(help="Short SMA window")]
LongWindowOption = Annotated[int, typer.Option(help="Long SMA window")]
TrainYearsOption = Annotated[int, typer.Option(help="Walk-forward training years")]
TestYearsOption = Annotated[int, typer.Option(help="Walk-forward testing years")]
CostOption = Annotated[float, typer.Option(help="Transaction cost in basis points")]
MonteCarloSimulationsOption = Annotated[
    int,
    typer.Option(help="Monte Carlo simulation count"),
]
MonteCarloSeedOption = Annotated[int, typer.Option(help="Monte Carlo random seed")]


@app.command()
def main(
    tickers: TickersOption = "AAPL,MSFT,NVDA",
    short_window: ShortWindowOption = 20,
    long_window: LongWindowOption = 50,
    train_years: TrainYearsOption = 3,
    test_years: TestYearsOption = 1,
    transaction_cost_bps: CostOption = 5.0,
    monte_carlo_simulations: MonteCarloSimulationsOption = 1000,
    monte_carlo_seed: MonteCarloSeedOption = 42,
) -> None:
    parameters = {
        "tickers": [ticker.strip().upper() for ticker in tickers.split(",")],
        "short_window": short_window,
        "long_window": long_window,
        "train_years": train_years,
        "test_years": test_years,
        "transaction_cost_bps": transaction_cost_bps,
        "monte_carlo_simulations": monte_carlo_simulations,
        "monte_carlo_seed": monte_carlo_seed,
    }

    manifest = build_experiment_manifest(
        experiment_name="sma_crossover_research_experiment",
        parameters=parameters,
        output_files=default_sma_manifest_outputs(),
    )

    output_path = project_path("reports", "backtests", "experiment_manifest.json")
    write_experiment_manifest(manifest, output_path)

    console.print("[bold green]Experiment manifest complete[/bold green]")
    console.print(f"Saved manifest: {output_path}")
    console.print(f"Git commit: {manifest['git_commit']}")
    console.print(f"Git status short: {manifest['git_status_short']!r}")


if __name__ == "__main__":
    app()
