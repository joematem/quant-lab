from __future__ import annotations

from rich.console import Console

from quantlab.data.duckdb_prices import (
    calculate_daily_returns,
    connect_duckdb,
    load_yahoo_prices,
    query_prices,
    summarize_prices,
)
from quantlab.utils.paths import project_path

console = Console()


def main() -> None:
    connection = connect_duckdb()
    load_yahoo_prices(connection)

    summary = summarize_prices(connection)
    returns = calculate_daily_returns(connection)
    aapl = query_prices(connection, ticker="AAPL", start="2024-01-01")

    reports_dir = project_path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_path = reports_dir / "yahoo_price_summary.csv"
    returns_path = reports_dir / "yahoo_daily_returns.csv"
    aapl_path = reports_dir / "aapl_prices_from_2024.csv"

    summary.to_csv(summary_path, index=False)
    returns.to_csv(returns_path, index=False)
    aapl.to_csv(aapl_path, index=False)

    console.print("[bold green]Yahoo DuckDB research query complete[/bold green]")
    console.print(summary)
    console.print(f"Saved summary: {summary_path}")
    console.print(f"Saved returns: {returns_path}")
    console.print(f"Saved AAPL sample: {aapl_path}")


if __name__ == "__main__":
    main()
