from __future__ import annotations

from rich.console import Console

from quantlab.data.duckdb_prices import (
    calculate_daily_returns,
    connect_duckdb,
    load_yahoo_prices,
)
from quantlab.research_performance import (
    calculate_cumulative_returns,
    summarize_performance,
)
from quantlab.utils.paths import project_path

console = Console()


def main() -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    returns = calculate_daily_returns(connection)

    performance_summary = summarize_performance(returns)
    cumulative_returns = calculate_cumulative_returns(returns)

    reports_dir = project_path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_path = reports_dir / "performance_summary.csv"
    cumulative_path = reports_dir / "cumulative_returns.csv"

    performance_summary.to_csv(summary_path, index=False)
    cumulative_returns.to_csv(cumulative_path, index=False)

    console.print("[bold green]Performance report complete[/bold green]")
    console.print(performance_summary)
    console.print(f"Saved performance summary: {summary_path}")
    console.print(f"Saved cumulative returns: {cumulative_path}")


if __name__ == "__main__":
    main()
