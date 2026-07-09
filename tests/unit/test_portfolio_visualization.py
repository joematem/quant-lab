from pathlib import Path

import pandas as pd
import pytest

from quantlab.visualization import plot_portfolio_strategy_comparison


def sample_portfolio_returns() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": [
                "equal_weight_sma",
                "equal_weight_sma",
                "equal_weight_buy_hold",
                "equal_weight_buy_hold",
            ],
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-01",
                "2024-01-02",
            ],
            "adj_close": [100.0, 101.0, 100.0, 102.0],
            "daily_return": [0.0, 0.01, 0.0, 0.02],
        }
    )


def test_plot_portfolio_strategy_comparison_creates_file(tmp_path: Path):
    output_path = tmp_path / "portfolio_chart.png"

    result = plot_portfolio_strategy_comparison(
        portfolio_returns=sample_portfolio_returns(),
        output_path=output_path,
    )

    assert result.exists()
    assert result.suffix == ".png"


def test_plot_portfolio_strategy_comparison_rejects_missing_columns(
    tmp_path: Path,
):
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        plot_portfolio_strategy_comparison(
            portfolio_returns=bad_data,
            output_path=tmp_path / "bad.png",
        )
