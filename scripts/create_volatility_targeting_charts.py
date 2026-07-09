from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.utils.paths import project_path
from quantlab.visualization import plot_portfolio_strategy_comparison

app = typer.Typer(help="Create volatility-targeted portfolio comparison charts.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    portfolio_path = reports_dir / "portfolio_equal_weight_returns.csv"
    targeted_path = reports_dir / "portfolio_volatility_targeted_returns.csv"

    if not portfolio_path.exists():
        raise FileNotFoundError(
            "Missing equal-weight portfolio returns. Run `make portfolio` first."
        )

    if not targeted_path.exists():
        raise FileNotFoundError(
            "Missing volatility-targeted returns. Run `make risk` first."
        )

    portfolio_returns = pd.read_csv(portfolio_path)
    targeted_returns = pd.read_csv(targeted_path)

    combined_returns = pd.concat(
        [portfolio_returns, targeted_returns],
        ignore_index=True,
    )

    output_path = figures_dir / "portfolio_volatility_targeted_comparison.png"

    plot_portfolio_strategy_comparison(
        portfolio_returns=combined_returns,
        output_path=output_path,
    )

    console.print("[bold green]Volatility-targeting chart complete[/bold green]")
    console.print(f"Saved chart: {output_path}")


if __name__ == "__main__":
    app()
