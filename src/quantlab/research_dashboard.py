from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quantlab.utils.paths import project_path


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load experiment manifest JSON."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest file: {manifest_path}")

    return json.loads(manifest_path.read_text())


def format_output_status(path: Path) -> str:
    """Return Markdown status for a local output file."""
    if path.exists():
        return "available"

    return "missing"


def create_research_dashboard(
    output_path: Path,
    manifest_path: Path,
) -> Path:
    """Create a Markdown dashboard/index for the research experiment."""
    manifest = load_manifest(manifest_path)

    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    report_files = [
        reports_dir / "sma_research_report.md",
        reports_dir / "experiment_manifest.json",
        reports_dir / "walk_forward_summary.csv",
        reports_dir / "portfolio_equal_weight_summary.csv",
        reports_dir / "portfolio_strategy_comparison_summary.csv",
        reports_dir / "portfolio_volatility_targeted_summary.csv",
        reports_dir / "transaction_cost_stress_summary.csv",
        reports_dir / "monte_carlo_portfolio_summary.csv",
    ]

    chart_files = [
        figures_dir / "walk_forward_sharpe.png",
        figures_dir / "walk_forward_selected_short_window.png",
        figures_dir / "walk_forward_selected_long_window.png",
        figures_dir / "multi_ticker_sma_vs_buy_hold.png",
        figures_dir / "portfolio_equal_weight_comparison.png",
        figures_dir / "portfolio_volatility_targeted_comparison.png",
        figures_dir / "transaction_cost_stress_sharpe.png",
        figures_dir / "transaction_cost_stress_total_return_decay.png",
        figures_dir / "monte_carlo_total_return_distribution.png",
        figures_dir / "monte_carlo_max_drawdown_distribution.png",
        figures_dir / "monte_carlo_sharpe_distribution.png",
    ]

    parameters = manifest.get("parameters", {})

    report_rows = "\n".join(
        f"| `{path}` | {format_output_status(path)} |" for path in report_files
    )

    chart_rows = "\n".join(
        f"| `{path}` | {format_output_status(path)} |" for path in chart_files
    )

    parameter_rows = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in parameters.items()
    )

    dashboard = f"""# Quant Lab Research Dashboard

## 1. Project status

This dashboard indexes the current SMA crossover research experiment.

Current phase status:

| Area | Status |
|---|---|
| Data ingestion | complete |
| Backtesting | complete |
| Benchmark comparison | complete |
| Parameter sweep | complete |
| Walk-forward validation | complete |
| Portfolio backtesting | complete |
| Volatility targeting | complete |
| Transaction-cost stress testing | complete |
| Monte Carlo robustness testing | complete |
| Research report | complete |
| Experiment manifest | complete |
| Strategy decision gate | pending |
| MT5 paper-trading prototype | not started |

## 2. Experiment identity

| Field | Value |
|---|---|
| Experiment name | `{manifest.get("experiment_name", "N/A")}` |
| Created at UTC | `{manifest.get("created_at_utc", "N/A")}` |
| Git commit | `{manifest.get("git_commit", "N/A")}` |
| Git status short | `{manifest.get("git_status_short", "N/A")}` |

## 3. Experiment parameters

| Parameter | Value |
|---|---|
{parameter_rows}

## 4. Research outputs

| File | Status |
|---|---|
{report_rows}

## 5. Chart outputs

| Chart | Status |
|---|---|
{chart_rows}

## 6. Current research interpretation

The current strategy research is useful but not approved for live trading.

The Monte Carlo robustness test shows substantial downside fragility,
including a high probability of drawdowns worse than 30 percent under
bootstrap simulation.

This means the correct next step is a formal decision gate, not live deployment.

## 7. Next step

Proceed to Step 39: strategy decision gate.

The strategy should be classified as one of:

1. Reject.
2. Continue research.
3. Approve for paper trading only.

Live trading remains out of scope.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard)

    return output_path
