from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.utils.paths import project_path
from quantlab.visualization import plot_transaction_cost_stress

app = typer.Typer(help="Create transaction cost stress charts.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    input_path = reports_dir / "transaction_cost_stress_summary.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing transaction cost stress summary. Run `make cost-stress` first."
        )

    stress_results = pd.read_csv(input_path)

    chart_specs = {
        "sharpe_ratio": figures_dir / "transaction_cost_stress_sharpe.png",
        "total_return_decay": figures_dir
        / "transaction_cost_stress_total_return_decay.png",
    }

    for metric, output_path in chart_specs.items():
        plot_transaction_cost_stress(
            stress_results=stress_results,
            metric=metric,
            output_path=output_path,
        )
        console.print(f"Saved {metric} chart: {output_path}")

    console.print("[bold green]Transaction cost stress charts complete[/bold green]")


if __name__ == "__main__":
    app()
