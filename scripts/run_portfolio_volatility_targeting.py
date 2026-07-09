from __future__ import annotations

from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from quantlab.risk.volatility_targeting import (
    apply_volatility_target,
    summarize_volatility_targeted_returns,
)
from quantlab.utils.paths import project_path

app = typer.Typer(help="Apply volatility targeting to portfolio returns.")
console = Console()

TargetVolOption = Annotated[
    float,
    typer.Option(help="Target annual volatility, e.g. 0.15 for 15%"),
]

LookbackOption = Annotated[int, typer.Option(help="Rolling volatility lookback days")]
MaxLeverageOption = Annotated[float, typer.Option(help="Maximum leverage cap")]


@app.command()
def main(
    target_annual_volatility: TargetVolOption = 0.15,
    lookback_days: LookbackOption = 63,
    max_leverage: MaxLeverageOption = 1.0,
) -> None:
    reports_dir = project_path("reports", "backtests")
    input_path = reports_dir / "portfolio_equal_weight_returns.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing portfolio returns. "
            "Run `uv run python scripts/run_equal_weight_portfolio_backtest.py` first."
        )

    portfolio_returns = pd.read_csv(input_path)
    sma_returns = portfolio_returns[
        portfolio_returns["ticker"] == "equal_weight_sma"
    ].copy()

    if sma_returns.empty:
        raise ValueError("No equal_weight_sma returns found.")

    targeted_returns = apply_volatility_target(
        returns=sma_returns,
        target_annual_volatility=target_annual_volatility,
        lookback_days=lookback_days,
        max_leverage=max_leverage,
        output_ticker="equal_weight_sma_vol_targeted",
    )

    summary = summarize_volatility_targeted_returns(targeted_returns)

    returns_path = reports_dir / "portfolio_volatility_targeted_returns.csv"
    summary_path = reports_dir / "portfolio_volatility_targeted_summary.csv"

    targeted_returns.to_csv(returns_path, index=False)
    summary.to_csv(summary_path, index=False)

    console.print("[bold green]Portfolio volatility targeting complete[/bold green]")
    console.print(summary)
    console.print(f"Saved targeted returns: {returns_path}")
    console.print(f"Saved targeted summary: {summary_path}")


if __name__ == "__main__":
    app()
