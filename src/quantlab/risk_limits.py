from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


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


def evaluate_research_risk_limits(
    portfolio_summary: pd.DataFrame,
    monte_carlo_summary: pd.DataFrame,
    decision_gate: dict[str, Any],
    limits: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Evaluate research risk limits for strategy eligibility."""
    _require_columns(
        portfolio_summary,
        {"ticker", "max_drawdown", "sharpe_ratio"},
        "portfolio_summary",
    )
    _require_columns(
        monte_carlo_summary,
        {
            "ticker",
            "max_drawdown_p50",
            "max_drawdown_p05",
            "probability_drawdown_worse_than_30pct",
        },
        "monte_carlo_summary",
    )

    active_limits = {
        "max_allowed_portfolio_drawdown": -0.30,
        "max_allowed_monte_carlo_median_drawdown": -0.25,
        "max_allowed_monte_carlo_tail_drawdown": -0.40,
        "max_allowed_drawdown_worse_than_30pct_probability": 0.25,
        "min_required_portfolio_sharpe": 0.50,
    }

    if limits is not None:
        active_limits.update(limits)

    strategy_row = portfolio_summary.iloc[0]
    monte_carlo_row = monte_carlo_summary.iloc[0]

    observed = {
        "portfolio_ticker": strategy_row["ticker"],
        "portfolio_max_drawdown": float(strategy_row["max_drawdown"]),
        "portfolio_sharpe_ratio": float(strategy_row["sharpe_ratio"]),
        "monte_carlo_ticker": monte_carlo_row["ticker"],
        "monte_carlo_median_drawdown": float(monte_carlo_row["max_drawdown_p50"]),
        "monte_carlo_tail_drawdown": float(monte_carlo_row["max_drawdown_p05"]),
        "monte_carlo_drawdown_worse_than_30pct_probability": float(
            monte_carlo_row["probability_drawdown_worse_than_30pct"]
        ),
        "decision_gate_decision": decision_gate.get("decision"),
        "decision_gate_paper_trading_allowed": bool(
            decision_gate.get("paper_trading_allowed")
        ),
        "decision_gate_live_trading_allowed": bool(
            decision_gate.get("live_trading_allowed")
        ),
    }

    checks = {
        "portfolio_drawdown_limit_ok": (
            observed["portfolio_max_drawdown"]
            >= active_limits["max_allowed_portfolio_drawdown"]
        ),
        "portfolio_sharpe_limit_ok": (
            observed["portfolio_sharpe_ratio"]
            >= active_limits["min_required_portfolio_sharpe"]
        ),
        "monte_carlo_median_drawdown_limit_ok": (
            observed["monte_carlo_median_drawdown"]
            >= active_limits["max_allowed_monte_carlo_median_drawdown"]
        ),
        "monte_carlo_tail_drawdown_limit_ok": (
            observed["monte_carlo_tail_drawdown"]
            >= active_limits["max_allowed_monte_carlo_tail_drawdown"]
        ),
        "monte_carlo_drawdown_probability_limit_ok": (
            observed["monte_carlo_drawdown_worse_than_30pct_probability"]
            <= active_limits["max_allowed_drawdown_worse_than_30pct_probability"]
        ),
        "decision_gate_allows_paper_trading": observed[
            "decision_gate_paper_trading_allowed"
        ],
        "decision_gate_blocks_live_trading": not observed[
            "decision_gate_live_trading_allowed"
        ],
    }

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    research_status = (
        "RISK_LIMITS_PASS_FOR_PAPER_REVIEW"
        if not failed_checks
        else "RISK_LIMITS_FAIL_CONTINUE_RESEARCH"
    )

    return {
        "research_status": research_status,
        "observed": observed,
        "limits": active_limits,
        "checks": checks,
        "failed_checks": failed_checks,
        "paper_trading_allowed": research_status == "RISK_LIMITS_PASS_FOR_PAPER_REVIEW",
        "live_trading_allowed": False,
        "interpretation": (
            "This risk limits report is a research control layer. It does "
            "not approve live trading. Live trading remains prohibited."
        ),
    }


def write_risk_limits_json(
    report: dict[str, Any],
    output_path: Path,
) -> Path:
    """Write risk limits report as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True))

    return output_path


def write_risk_limits_markdown(
    report: dict[str, Any],
    output_path: Path,
) -> Path:
    """Write risk limits report as Markdown."""
    observed_rows = "\n".join(
        f"| `{name}` | `{value}` |" for name, value in report["observed"].items()
    )

    limit_rows = "\n".join(
        f"| `{name}` | `{value}` |" for name, value in report["limits"].items()
    )

    check_rows = "\n".join(
        f"| `{name}` | `{value}` |" for name, value in report["checks"].items()
    )

    failed_rows = "\n".join(f"- `{name}`" for name in report["failed_checks"])

    if not failed_rows:
        failed_rows = "- None"

    markdown = f"""# Research Risk Limits Report

## 1. Risk status

| Field | Value |
|---|---|
| Research status | `{report["research_status"]}` |
| Paper trading allowed | `{report["paper_trading_allowed"]}` |
| Live trading allowed | `{report["live_trading_allowed"]}` |

## 2. Observed risk metrics

| Metric | Value |
|---|---|
{observed_rows}

## 3. Risk limits

| Limit | Value |
|---|---|
{limit_rows}

## 4. Risk checks

| Check | Passed |
|---|---|
{check_rows}

## 5. Failed checks

{failed_rows}

## 6. Interpretation

{report["interpretation"]}

This model is designed to prevent premature deployment.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)

    return output_path
