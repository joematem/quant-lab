import pandas as pd
import pytest

from quantlab.backtesting.cost_stress import summarize_transaction_cost_stress


def sample_stress_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "transaction_cost_bps": [5.0, 25.0, 5.0, 25.0],
            "total_return": [1.0, 0.8, 0.5, 0.3],
            "annualized_return": [0.15, 0.12, 0.10, 0.07],
            "annualized_volatility": [0.20, 0.20, 0.18, 0.18],
            "sharpe_ratio": [0.75, 0.60, 0.55, 0.40],
            "max_drawdown": [-0.20, -0.22, -0.18, -0.19],
        }
    )


def test_summarize_transaction_cost_stress_returns_decay_columns():
    result = summarize_transaction_cost_stress(sample_stress_results())

    assert not result.empty
    assert "total_return_decay" in result.columns
    assert "sharpe_ratio_decay" in result.columns

    aapl_25 = result[
        (result["ticker"] == "AAPL") & (result["transaction_cost_bps"] == 25.0)
    ].iloc[0]

    assert aapl_25["total_return_decay"] == pytest.approx(-0.2)
    assert aapl_25["sharpe_ratio_decay"] == pytest.approx(-0.15)


def test_summarize_transaction_cost_stress_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        summarize_transaction_cost_stress(bad_data)
