from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quantlab.utils.paths import project_path


def file_sha256(path: Path) -> str:
    """Return SHA256 hash for a file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def get_git_commit() -> str:
    """Return current Git commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def get_git_status() -> str:
    """Return short Git status."""
    result = subprocess.run(
        ["git", "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def build_experiment_manifest(
    experiment_name: str,
    parameters: dict[str, Any],
    output_files: list[Path],
) -> dict[str, Any]:
    """Build a reproducibility manifest for an experiment."""
    manifest_outputs = []

    for output_file in output_files:
        if output_file.exists():
            manifest_outputs.append(
                {
                    "path": str(output_file),
                    "sha256": file_sha256(output_file),
                    "bytes": output_file.stat().st_size,
                }
            )
        else:
            manifest_outputs.append(
                {
                    "path": str(output_file),
                    "missing": True,
                }
            )

    return {
        "experiment_name": experiment_name,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": get_git_commit(),
        "git_status_short": get_git_status(),
        "parameters": parameters,
        "outputs": manifest_outputs,
    }


def write_experiment_manifest(
    manifest: dict[str, Any],
    output_path: Path,
) -> Path:
    """Write experiment manifest as formatted JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))

    return output_path


def default_sma_manifest_outputs() -> list[Path]:
    """Return default output files for the SMA research experiment."""
    reports_dir = project_path("reports", "backtests")
    figures_dir = reports_dir / "figures"

    return [
        reports_dir / "sma_research_report.md",
        reports_dir / "walk_forward_summary.csv",
        reports_dir / "portfolio_equal_weight_summary.csv",
        reports_dir / "portfolio_strategy_comparison_summary.csv",
        reports_dir / "portfolio_volatility_targeted_summary.csv",
        reports_dir / "transaction_cost_stress_summary.csv",
        reports_dir / "monte_carlo_portfolio_summary.csv",
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
