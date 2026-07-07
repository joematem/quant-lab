from __future__ import annotations

from rich.console import Console

from quantlab.data.duckdb_prices import (
    calculate_daily_returns,
    connect_duckdb,
    load_yahoo_prices,
)
from quantlab.research_performance import (
    calculate_cumulative_returns,
    calculate_drawdowns,
)
from quantlab.utils.paths import project_path
from quantlab.visualization import plot_cumulative_returns, plot_drawdowns

console = Console()


def main() -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    returns = calculate_daily_returns(connection)
    cumulative_returns = calculate_cumulative_returns(returns)
    drawdowns = calculate_drawdowns(returns)

    figures_dir = project_path("reports", "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    cumulative_chart_path = figures_dir / "cumulative_returns.png"
    drawdown_chart_path = figures_dir / "drawdowns.png"

    plot_cumulative_returns(cumulative_returns, cumulative_chart_path)
    plot_drawdowns(drawdowns, drawdown_chart_path)

    console.print("[bold green]Performance charts complete[/bold green]")
    console.print(f"Saved cumulative returns chart: {cumulative_chart_path}")
    console.print(f"Saved drawdown chart: {drawdown_chart_path}")


if __name__ == "__main__":
    main()
