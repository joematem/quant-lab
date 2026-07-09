from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_cumulative_returns(
    cumulative_returns: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Plot cumulative returns by ticker and save chart."""
    required_columns = {"ticker", "date", "cumulative_return"}
    missing = required_columns - set(cumulative_returns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    for ticker, group in cumulative_returns.groupby("ticker"):
        ordered = group.sort_values("date")
        ax.plot(
            ordered["date"],
            ordered["cumulative_return"],
            label=ticker,
        )

    ax.set_title("Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_drawdowns(
    drawdowns: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Plot drawdowns by ticker and save chart."""
    required_columns = {"ticker", "date", "drawdown"}
    missing = required_columns - set(drawdowns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    for ticker, group in drawdowns.groupby("ticker"):
        ordered = group.sort_values("date")
        ax.plot(
            ordered["date"],
            ordered["drawdown"],
            label=ticker,
        )

    ax.set_title("Drawdowns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_strategy_comparison(
    comparison: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Plot strategy versus benchmark cumulative returns."""
    required_columns = {"strategy", "date", "cumulative_return"}
    missing = required_columns - set(comparison.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    for strategy, group in comparison.groupby("strategy"):
        ordered = group.sort_values("date")
        ax.plot(
            ordered["date"],
            ordered["cumulative_return"],
            label=strategy,
        )

    ax.set_title("Strategy Comparison: SMA Crossover vs Buy-and-Hold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_multi_ticker_strategy_comparison(
    comparison: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Plot multi-ticker strategy comparison using cumulative returns."""
    required_columns = {"ticker", "strategy", "date", "cumulative_return"}
    missing = required_columns - set(comparison.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = comparison.copy()
    plot_data["label"] = plot_data["ticker"] + " - " + plot_data["strategy"]

    fig, ax = plt.subplots(figsize=(14, 8))

    for label, group in plot_data.groupby("label"):
        ordered = group.sort_values("date")
        ax.plot(
            ordered["date"],
            ordered["cumulative_return"],
            label=label,
        )

    ax.set_title("Multi-Ticker Strategy Comparison: SMA vs Buy-and-Hold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_walk_forward_metric(
    walk_forward_results: pd.DataFrame,
    metric: str,
    output_path: Path,
) -> Path:
    """Plot a walk-forward metric over test years by ticker."""
    required_columns = {"ticker", "test_start_year", metric}
    missing = required_columns - set(walk_forward_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    for ticker, group in walk_forward_results.groupby("ticker"):
        ordered = group.sort_values("test_start_year")
        ax.plot(
            ordered["test_start_year"],
            ordered[metric],
            marker="o",
            label=ticker,
        )

    ax.set_title(f"Walk-Forward {metric.replace('_', ' ').title()}")
    ax.set_xlabel("Test start year")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path
