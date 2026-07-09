from __future__ import annotations

import pandas as pd

REQUIRED_COST_STRESS_COLUMNS = {
    "ticker",
    "transaction_cost_bps",
    "total_return",
    "annualized_return",
    "annualized_volatility",
    "sharpe_ratio",
    "max_drawdown",
}


def summarize_transaction_cost_stress(
    stress_results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize strategy robustness across transaction cost assumptions."""
    missing = REQUIRED_COST_STRESS_COLUMNS - set(stress_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    summary = stress_results.copy()

    summary = summary.sort_values(
        ["ticker", "transaction_cost_bps"],
        ascending=[True, True],
    ).reset_index(drop=True)

    baseline = summary.groupby("ticker").first().reset_index()
    baseline = baseline[
        [
            "ticker",
            "total_return",
            "annualized_return",
            "sharpe_ratio",
            "max_drawdown",
        ]
    ].rename(
        columns={
            "total_return": "baseline_total_return",
            "annualized_return": "baseline_annualized_return",
            "sharpe_ratio": "baseline_sharpe_ratio",
            "max_drawdown": "baseline_max_drawdown",
        }
    )

    merged = summary.merge(baseline, on="ticker", how="left")

    merged["total_return_decay"] = (
        merged["total_return"] - merged["baseline_total_return"]
    )
    merged["sharpe_ratio_decay"] = (
        merged["sharpe_ratio"] - merged["baseline_sharpe_ratio"]
    )

    return merged.sort_values(
        ["transaction_cost_bps", "sharpe_ratio"],
        ascending=[True, False],
    ).reset_index(drop=True)
