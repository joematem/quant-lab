from pathlib import Path

import pandas as pd
import pytest

from quantlab.visualization import plot_monte_carlo_distribution


def sample_monte_carlo_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["equal_weight_sma_monte_carlo"] * 5,
            "simulation_id": [1, 2, 3, 4, 5],
            "total_return": [0.10, 0.20, -0.05, 0.15, 0.05],
            "max_drawdown": [-0.10, -0.20, -0.15, -0.08, -0.12],
            "sharpe_ratio": [0.5, 0.8, -0.2, 0.7, 0.3],
        }
    )


def test_plot_monte_carlo_distribution_creates_file(tmp_path: Path):
    output_path = tmp_path / "monte_carlo_total_return.png"

    result = plot_monte_carlo_distribution(
        monte_carlo_results=sample_monte_carlo_results(),
        metric="total_return",
        output_path=output_path,
    )

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_monte_carlo_distribution_rejects_missing_columns(
    tmp_path: Path,
):
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma_monte_carlo"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_monte_carlo_distribution(
            monte_carlo_results=bad_data,
            metric="total_return",
            output_path=tmp_path / "bad.png",
        )
