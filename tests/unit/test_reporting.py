from pathlib import Path

import pandas as pd
import pytest

from quantlab.reporting import create_sma_research_report


def sample_walk_forward_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            "walk_forward_windows": [9, 9],
            "mean_test_total_return": [0.15, 0.03],
            "positive_return_rate": [0.67, 0.44],
            "mean_test_sharpe_ratio": [0.88, 0.17],
            "positive_sharpe_rate": [0.67, 0.44],
            "mean_test_max_drawdown": [-0.15, -0.12],
            "worst_test_max_drawdown": [-0.32, -0.18],
            "most_common_short_window": [5, 50],
            "most_common_long_window": [50, 100],
            "parameter_change_count": [5, 7],
        }
    )


def test_create_sma_research_report_creates_markdown_file(tmp_path: Path):
    output_path = tmp_path / "sma_research_report.md"

    result = create_sma_research_report(
        sample_walk_forward_summary(),
        output_path,
    )

    assert result.exists()
    assert result.suffix == ".md"

    text = result.read_text()
    assert "SMA Crossover Strategy Research Report" in text
    assert "Walk-forward robustness summary" in text


def test_create_sma_research_report_rejects_missing_columns(tmp_path: Path):
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        create_sma_research_report(
            bad_data,
            tmp_path / "bad_report.md",
        )
