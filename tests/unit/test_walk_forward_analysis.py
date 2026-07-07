import pandas as pd
import pytest

from quantlab.backtesting.walk_forward_analysis import (
    summarize_walk_forward_results,
)


def sample_walk_forward_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "train_start_year": [2015, 2016, 2015, 2016],
            "train_end_year": [2017, 2018, 2017, 2018],
            "test_start_year": [2018, 2019, 2018, 2019],
            "test_end_year": [2018, 2019, 2018, 2019],
            "selected_short_window": [20, 20, 10, 30],
            "selected_long_window": [100, 100, 50, 150],
            "test_total_return": [0.10, -0.05, 0.20, 0.05],
            "test_sharpe_ratio": [1.2, -0.5, 1.5, None],
            "test_max_drawdown": [-0.10, -0.20, -0.08, -0.12],
        }
    )


def test_summarize_walk_forward_results_returns_summary():
    summary = summarize_walk_forward_results(sample_walk_forward_results())

    assert set(summary["ticker"]) == {"AAPL", "MSFT"}
    assert "mean_test_sharpe_ratio" in summary.columns
    assert "positive_return_rate" in summary.columns
    assert "parameter_change_count" in summary.columns


def test_summarize_walk_forward_results_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        summarize_walk_forward_results(bad_data)
