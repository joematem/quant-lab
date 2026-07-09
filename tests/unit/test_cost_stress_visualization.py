from pathlib import Path

import pandas as pd
import pytest

from quantlab.visualization import plot_transaction_cost_stress


def sample_cost_stress_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "transaction_cost_bps": [5.0, 25.0, 5.0, 25.0],
            "sharpe_ratio": [0.8, 0.6, 0.7, 0.5],
            "total_return_decay": [0.0, -0.2, 0.0, -0.1],
        }
    )


def test_plot_transaction_cost_stress_creates_file(tmp_path: Path):
    output_path = tmp_path / "cost_stress.png"

    result = plot_transaction_cost_stress(
        stress_results=sample_cost_stress_results(),
        metric="sharpe_ratio",
        output_path=output_path,
    )

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_transaction_cost_stress_rejects_missing_columns(tmp_path: Path):
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_transaction_cost_stress(
            stress_results=bad_data,
            metric="sharpe_ratio",
            output_path=tmp_path / "bad.png",
        )
