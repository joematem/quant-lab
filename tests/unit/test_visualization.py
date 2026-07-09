from pathlib import Path

import pandas as pd
import pytest

from quantlab.visualization import (
    plot_cumulative_returns,
    plot_drawdowns,
    plot_multi_ticker_strategy_comparison,
    plot_strategy_comparison,
    plot_walk_forward_metric,
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


def test_plot_multi_ticker_strategy_comparison_creates_file(tmp_path: Path):
    comparison = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "strategy": [
                "buy_and_hold",
                "sma_crossover",
                "buy_and_hold",
                "sma_crossover",
            ],
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01"]
            ),
            "cumulative_return": [0.02, 0.01, 0.03, 0.015],
        }
    )

    output_path = tmp_path / "multi_ticker_comparison.png"

    result = plot_multi_ticker_strategy_comparison(comparison, output_path)

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_multi_ticker_strategy_comparison_rejects_missing_columns(
    tmp_path: Path,
):
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_multi_ticker_strategy_comparison(bad_data, tmp_path / "bad.png")


def test_plot_walk_forward_metric_creates_file(tmp_path: Path):
    walk_forward_results = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "test_start_year": [2020, 2021, 2020, 2021],
            "test_sharpe_ratio": [1.0, 0.5, -0.2, 1.2],
        }
    )

    output_path = tmp_path / "walk_forward_sharpe.png"

    result = plot_walk_forward_metric(
        walk_forward_results,
        metric="test_sharpe_ratio",
        output_path=output_path,
    )

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_walk_forward_metric_rejects_missing_columns(tmp_path: Path):
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_walk_forward_metric(
            bad_data,
            metric="test_sharpe_ratio",
            output_path=tmp_path / "bad.png",
        )
