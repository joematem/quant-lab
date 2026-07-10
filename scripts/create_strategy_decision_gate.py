from __future__ import annotations

import pandas as pd
import typer
from rich.console import Console

from quantlab.decision_gate import (
    build_strategy_decision,
    write_strategy_decision_json,
    write_strategy_decision_markdown,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create strategy decision gate.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")

    walk_forward_summary = pd.read_csv(reports_dir / "walk_forward_summary.csv")
    monte_carlo_summary = pd.read_csv(reports_dir / "monte_carlo_portfolio_summary.csv")
    transaction_cost_stress = pd.read_csv(
        reports_dir / "transaction_cost_stress_summary.csv"
    )

    decision = build_strategy_decision(
        walk_forward_summary=walk_forward_summary,
        monte_carlo_summary=monte_carlo_summary,
        transaction_cost_stress=transaction_cost_stress,
    )

    json_path = reports_dir / "strategy_decision_gate.json"
    markdown_path = reports_dir / "strategy_decision_gate.md"

    write_strategy_decision_json(decision, json_path)
    write_strategy_decision_markdown(decision, markdown_path)

    console.print("[bold green]Strategy decision gate complete[/bold green]")
    console.print(f"Decision: {decision['decision']}")
    console.print(f"Paper trading allowed: {decision['paper_trading_allowed']}")
    console.print(f"Live trading allowed: {decision['live_trading_allowed']}")
    console.print(f"Saved JSON: {json_path}")
    console.print(f"Saved Markdown: {markdown_path}")


if __name__ == "__main__":
    app()
