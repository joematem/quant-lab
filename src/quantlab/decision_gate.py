from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

DECISION_REJECT = "REJECT"
DECISION_CONTINUE_RESEARCH = "CONTINUE_RESEARCH"
DECISION_APPROVE_FOR_PAPER_TRADING = "APPROVE_FOR_PAPER_TRADING"


def _require_columns(
    data: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in {dataset_name}: {sorted(missing)}"
        )


def build_strategy_decision(
    walk_forward_summary: pd.DataFrame,
    monte_carlo_summary: pd.DataFrame,
    transaction_cost_stress: pd.DataFrame,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Build a formal strategy research decision."""
    _require_columns(
        walk_forward_summary,
        {"ticker", "mean_test_sharpe_ratio", "positive_return_rate"},
        "walk_forward_summary",
    )
    _require_columns(
        monte_carlo_summary,
        {
            "ticker",
            "sharpe_ratio_p05",
            "sharpe_ratio_p50",
            "probability_positive_return",
            "probability_negative_return",
            "probability_drawdown_worse_than_30pct",
        },
        "monte_carlo_summary",
    )
    _require_columns(
        transaction_cost_stress,
        {"ticker", "transaction_cost_bps", "sharpe_ratio"},
        "transaction_cost_stress",
    )

    active_thresholds = {
        "approval_min_walk_forward_sharpe": 0.50,
        "approval_min_positive_return_rate": 0.60,
        "approval_min_monte_carlo_p05_sharpe": 0.00,
        "approval_min_monte_carlo_positive_return_probability": 0.70,
        "approval_max_drawdown_worse_than_30pct_probability": 0.25,
        "approval_min_high_cost_sharpe": 0.25,
        "rejection_max_drawdown_worse_than_30pct_probability": 0.75,
        "rejection_max_negative_return_probability": 0.50,
        "rejection_min_monte_carlo_p50_sharpe": 0.00,
    }

    if thresholds is not None:
        active_thresholds.update(thresholds)

    best_walk_forward = walk_forward_summary.sort_values(
        "mean_test_sharpe_ratio",
        ascending=False,
    ).iloc[0]

    monte_carlo = monte_carlo_summary.iloc[0]

    max_cost = transaction_cost_stress["transaction_cost_bps"].max()
    high_cost_results = transaction_cost_stress[
        transaction_cost_stress["transaction_cost_bps"] == max_cost
    ]
    high_cost_min_sharpe = float(high_cost_results["sharpe_ratio"].min())

    metrics = {
        "best_walk_forward_ticker": best_walk_forward["ticker"],
        "best_walk_forward_mean_sharpe": float(
            best_walk_forward["mean_test_sharpe_ratio"]
        ),
        "best_walk_forward_positive_return_rate": float(
            best_walk_forward["positive_return_rate"]
        ),
        "monte_carlo_p05_sharpe": float(monte_carlo["sharpe_ratio_p05"]),
        "monte_carlo_p50_sharpe": float(monte_carlo["sharpe_ratio_p50"]),
        "monte_carlo_positive_return_probability": float(
            monte_carlo["probability_positive_return"]
        ),
        "monte_carlo_negative_return_probability": float(
            monte_carlo["probability_negative_return"]
        ),
        "monte_carlo_drawdown_worse_than_30pct_probability": float(
            monte_carlo["probability_drawdown_worse_than_30pct"]
        ),
        "high_cost_bps": float(max_cost),
        "high_cost_min_sharpe": high_cost_min_sharpe,
    }

    rejection_reasons = []
    paper_trading_blockers = []

    if (
        metrics["monte_carlo_drawdown_worse_than_30pct_probability"]
        > active_thresholds["rejection_max_drawdown_worse_than_30pct_probability"]
    ):
        rejection_reasons.append(
            "Monte Carlo drawdown risk exceeds rejection threshold."
        )

    if (
        metrics["monte_carlo_negative_return_probability"]
        > active_thresholds["rejection_max_negative_return_probability"]
    ):
        rejection_reasons.append(
            "Monte Carlo negative-return probability exceeds rejection threshold."
        )

    if (
        metrics["monte_carlo_p50_sharpe"]
        <= active_thresholds["rejection_min_monte_carlo_p50_sharpe"]
    ):
        rejection_reasons.append("Median Monte Carlo Sharpe ratio is not positive.")

    approval_checks = {
        "walk_forward_sharpe_ok": (
            metrics["best_walk_forward_mean_sharpe"]
            >= active_thresholds["approval_min_walk_forward_sharpe"]
        ),
        "positive_return_rate_ok": (
            metrics["best_walk_forward_positive_return_rate"]
            >= active_thresholds["approval_min_positive_return_rate"]
        ),
        "monte_carlo_p05_sharpe_ok": (
            metrics["monte_carlo_p05_sharpe"]
            >= active_thresholds["approval_min_monte_carlo_p05_sharpe"]
        ),
        "monte_carlo_positive_return_probability_ok": (
            metrics["monte_carlo_positive_return_probability"]
            >= active_thresholds["approval_min_monte_carlo_positive_return_probability"]
        ),
        "monte_carlo_drawdown_risk_ok": (
            metrics["monte_carlo_drawdown_worse_than_30pct_probability"]
            <= active_thresholds["approval_max_drawdown_worse_than_30pct_probability"]
        ),
        "high_cost_sharpe_ok": (
            metrics["high_cost_min_sharpe"]
            >= active_thresholds["approval_min_high_cost_sharpe"]
        ),
    }

    for check_name, passed in approval_checks.items():
        if not passed:
            paper_trading_blockers.append(check_name)

    if rejection_reasons:
        decision = DECISION_REJECT
    elif all(approval_checks.values()):
        decision = DECISION_APPROVE_FOR_PAPER_TRADING
    else:
        decision = DECISION_CONTINUE_RESEARCH

    return {
        "decision": decision,
        "metrics": metrics,
        "thresholds": active_thresholds,
        "approval_checks": approval_checks,
        "rejection_reasons": rejection_reasons,
        "paper_trading_blockers": paper_trading_blockers,
        "live_trading_allowed": False,
        "paper_trading_allowed": decision == DECISION_APPROVE_FOR_PAPER_TRADING,
        "interpretation": (
            "This is a research decision gate. It does not approve live "
            "trading. Paper trading is allowed only if all approval checks pass."
        ),
    }


def write_strategy_decision_json(
    decision: dict[str, Any],
    output_path: Path,
) -> Path:
    """Write strategy decision as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(decision, indent=2, sort_keys=True))

    return output_path


def write_strategy_decision_markdown(
    decision: dict[str, Any],
    output_path: Path,
) -> Path:
    """Write strategy decision as Markdown."""
    metrics = decision["metrics"]
    thresholds = decision["thresholds"]
    approval_checks = decision["approval_checks"]

    approval_rows = "\n".join(
        f"| `{name}` | `{passed}` |" for name, passed in approval_checks.items()
    )

    blocker_rows = "\n".join(
        f"- `{blocker}`" for blocker in decision["paper_trading_blockers"]
    )

    if not blocker_rows:
        blocker_rows = "- None"

    rejection_rows = "\n".join(
        f"- {reason}" for reason in decision["rejection_reasons"]
    )

    if not rejection_rows:
        rejection_rows = "- None"

    threshold_rows = "\n".join(
        f"| `{name}` | `{value}` |" for name, value in thresholds.items()
    )

    metric_rows = "\n".join(
        f"| `{name}` | `{value}` |" for name, value in metrics.items()
    )

    markdown = f"""# Strategy Decision Gate

## 1. Decision

| Field | Value |
|---|---|
| Decision | `{decision["decision"]}` |
| Paper trading allowed | `{decision["paper_trading_allowed"]}` |
| Live trading allowed | `{decision["live_trading_allowed"]}` |

## 2. Metrics used

| Metric | Value |
|---|---|
{metric_rows}

## 3. Approval checks

| Check | Passed |
|---|---|
{approval_rows}

## 4. Paper-trading blockers

{blocker_rows}

## 5. Rejection reasons

{rejection_rows}

## 6. Thresholds

| Threshold | Value |
|---|---|
{threshold_rows}

## 7. Interpretation

{decision["interpretation"]}

The strategy must not be deployed live from this research state.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)

    return output_path
