from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.utils.paths import project_path
from quantlab.visualization import plot_portfolio_strategy_comparison

app = typer.Typer(help="Create portfolio-level backtest charts.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    input_path = reports_dir / "portfolio_equal_weight_returns.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing portfolio returns. "
            "Run `uv run python scripts/run_equal_weight_portfolio_backtest.py` first."
        )

    portfolio_returns = pd.read_csv(input_path)

    output_path = figures_dir / "portfolio_equal_weight_comparison.png"

    plot_portfolio_strategy_comparison(
        portfolio_returns=portfolio_returns,
        output_path=output_path,
    )

    console.print("[bold green]Portfolio chart complete[/bold green]")
    console.print(f"Saved chart: {output_path}")


if __name__ == "__main__":
    app()
