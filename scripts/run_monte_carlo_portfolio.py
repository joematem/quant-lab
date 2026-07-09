from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.risk.monte_carlo import (
    run_return_bootstrap_monte_carlo,
    summarize_monte_carlo_results,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Run Monte Carlo robustness test on portfolio returns.")
console = Console()

SimulationsOption = Annotated[int, typer.Option(help="Number of simulations")]
SeedOption = Annotated[int, typer.Option(help="Random seed")]


@app.command()
def main(
    simulations: SimulationsOption = 1000,
    seed: SeedOption = 42,
) -> None:
    reports_dir = project_path("reports", "backtests")
    input_path = reports_dir / "portfolio_equal_weight_returns.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing portfolio returns. Run `make portfolio` first."
        )

    portfolio_returns = pd.read_csv(input_path)
    sma_returns = portfolio_returns[
        portfolio_returns["ticker"] == "equal_weight_sma"
    ].copy()

    if sma_returns.empty:
        raise ValueError("No equal_weight_sma returns found.")

    monte_carlo_results = run_return_bootstrap_monte_carlo(
        returns=sma_returns,
        simulations=simulations,
        seed=seed,
        output_ticker="equal_weight_sma_monte_carlo",
    )

    summary = summarize_monte_carlo_results(monte_carlo_results)

    results_path = reports_dir / "monte_carlo_portfolio_results.csv"
    summary_path = reports_dir / "monte_carlo_portfolio_summary.csv"

    monte_carlo_results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)

    console.print("[bold green]Monte Carlo portfolio test complete[/bold green]")
    console.print(summary)
    console.print(f"Saved Monte Carlo results: {results_path}")
    console.print(f"Saved Monte Carlo summary: {summary_path}")


if __name__ == "__main__":
    app()
