from pathlib import Path

import pandas as pd
import pytest

from quantlab.visualization import (
    plot_cumulative_returns,
    plot_drawdowns,
    plot_strategy_comparison,
)


def test_plot_cumulative_returns_creates_file(tmp_path: Path):
    cumulative_returns = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]
            ),
            "cumulative_return": [0.0, 0.01, 0.0, 0.02],
        }
    )

    output_path = tmp_path / "cumulative_returns.png"

    result = plot_cumulative_returns(cumulative_returns, output_path)

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_drawdowns_creates_file(tmp_path: Path):
    drawdowns = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]
            ),
            "drawdown": [0.0, -0.01, 0.0, -0.02],
        }
    )

    output_path = tmp_path / "drawdowns.png"

    result = plot_drawdowns(drawdowns, output_path)

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_cumulative_returns_rejects_missing_columns(tmp_path: Path):
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_cumulative_returns(bad_data, tmp_path / "bad.png")


def test_plot_strategy_comparison_creates_file(tmp_path: Path):
    comparison = pd.DataFrame(
        {
            "strategy": [
                "buy_and_hold",
                "buy_and_hold",
                "sma_crossover",
                "sma_crossover",
            ],
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]
            ),
            "cumulative_return": [0.0, 0.02, 0.0, 0.01],
        }
    )

    output_path = tmp_path / "comparison.png"

    result = plot_strategy_comparison(comparison, output_path)

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_strategy_comparison_rejects_missing_columns(tmp_path: Path):
    bad_data = pd.DataFrame({"strategy": ["buy_and_hold"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_strategy_comparison(bad_data, tmp_path / "bad.png")
