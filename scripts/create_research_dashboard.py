from __future__ import annotations

import typer
from rich.console import Console

from quantlab.research_dashboard import create_research_dashboard
from quantlab.utils.paths import project_path

app = typer.Typer(help="Create final research dashboard.")
console = Console()


@app.command()
def main() -> None:
    reports_dir = project_path("reports", "backtests")

    manifest_path = reports_dir / "experiment_manifest.json"
    output_path = reports_dir / "research_dashboard.md"

    create_research_dashboard(
        output_path=output_path,
        manifest_path=manifest_path,
    )

    console.print("[bold green]Research dashboard complete[/bold green]")
    console.print(f"Saved dashboard: {output_path}")


if __name__ == "__main__":
    app()
