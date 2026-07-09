from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.backtesting.portfolio_analysis import (
    create_portfolio_strategy_ranking,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create portfolio strategy comparison summary.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")

    portfolio_summary_path = reports_dir / "portfolio_equal_weight_summary.csv"
    targeted_summary_path = reports_dir / "portfolio_volatility_targeted_summary.csv"

    if not portfolio_summary_path.exists():
        raise FileNotFoundError(
            "Missing equal-weight portfolio summary. Run `make portfolio` first."
        )

    if not targeted_summary_path.exists():
        raise FileNotFoundError(
            "Missing volatility-targeted summary. Run `make risk` first."
        )

    portfolio_summary = pd.read_csv(portfolio_summary_path)
    targeted_summary = pd.read_csv(targeted_summary_path)

    combined_summary = pd.concat(
        [portfolio_summary, targeted_summary],
        ignore_index=True,
    )

    ranking = create_portfolio_strategy_ranking(combined_summary)

    output_path = reports_dir / "portfolio_strategy_comparison_summary.csv"
    ranking.to_csv(output_path, index=False)

    console.print("[bold green]Portfolio strategy comparison complete[/bold green]")
    console.print(ranking)
    console.print(f"Saved strategy comparison: {output_path}")


if __name__ == "__main__":
    app()
