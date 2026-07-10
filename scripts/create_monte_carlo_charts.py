from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.utils.paths import project_path
from quantlab.visualization import plot_monte_carlo_distribution

app = typer.Typer(help="Create Monte Carlo robustness charts.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    input_path = reports_dir / "monte_carlo_portfolio_results.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing Monte Carlo results. Run `make monte-carlo` first."
        )

    monte_carlo_results = pd.read_csv(input_path)

    chart_specs = {
        "total_return": figures_dir / "monte_carlo_total_return_distribution.png",
        "max_drawdown": figures_dir / "monte_carlo_max_drawdown_distribution.png",
        "sharpe_ratio": figures_dir / "monte_carlo_sharpe_distribution.png",
    }

    for metric, output_path in chart_specs.items():
        plot_monte_carlo_distribution(
            monte_carlo_results=monte_carlo_results,
            metric=metric,
            output_path=output_path,
        )
        console.print(f"Saved {metric} chart: {output_path}")

    console.print("[bold green]Monte Carlo charts complete[/bold green]")


if __name__ == "__main__":
    app()
