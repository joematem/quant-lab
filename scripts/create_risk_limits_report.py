from __future__ import annotations

import json

import pandas as pd
import typer
from rich.console import Console

from quantlab.risk_limits import (
    evaluate_research_risk_limits,
    write_risk_limits_json,
    write_risk_limits_markdown,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create research risk limits report.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")

    portfolio_summary = pd.read_csv(reports_dir / "portfolio_equal_weight_summary.csv")
    monte_carlo_summary = pd.read_csv(reports_dir / "monte_carlo_portfolio_summary.csv")
    decision_gate = json.loads(
        (reports_dir / "strategy_decision_gate.json").read_text()
    )

    report = evaluate_research_risk_limits(
        portfolio_summary=portfolio_summary,
        monte_carlo_summary=monte_carlo_summary,
        decision_gate=decision_gate,
    )

    json_path = reports_dir / "risk_limits_report.json"
    markdown_path = reports_dir / "risk_limits_report.md"

    write_risk_limits_json(report, json_path)
    write_risk_limits_markdown(report, markdown_path)

    console.print("[bold green]Risk limits report complete[/bold green]")
    console.print(f"Research status: {report['research_status']}")
    console.print(f"Paper trading allowed: {report['paper_trading_allowed']}")
    console.print(f"Live trading allowed: {report['live_trading_allowed']}")
    console.print(f"Saved JSON: {json_path}")
    console.print(f"Saved Markdown: {markdown_path}")


if __name__ == "__main__":
    app()
