import pandas as pd
import pytest

from quantlab.risk.volatility_targeting import (
    apply_volatility_target,
    summarize_volatility_targeted_returns,
)


def sample_returns() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    returns = [0.001, -0.002, 0.003, -0.001] * 25

    return pd.DataFrame(
        {
            "ticker": ["equal_weight_sma"] * len(dates),
            "date": dates,
            "daily_return": returns,
        }
    )


def test_apply_volatility_target_returns_scaled_series():
    result = apply_volatility_target(
        returns=sample_returns(),
        target_annual_volatility=0.15,
        lookback_days=20,
        max_leverage=1.0,
        output_ticker="equal_weight_sma_vol_targeted",
    )

    assert not result.empty
    assert set(result["ticker"]) == {"equal_weight_sma_vol_targeted"}
    assert "volatility_scale" in result.columns
    assert "adj_close" in result.columns
    assert result["volatility_scale"].max() <= 1.0


def test_summarize_volatility_targeted_returns():
    targeted = apply_volatility_target(
        returns=sample_returns(),
        target_annual_volatility=0.15,
        lookback_days=20,
        max_leverage=1.0,
        output_ticker="equal_weight_sma_vol_targeted",
    )

    summary = summarize_volatility_targeted_returns(targeted)

    assert not summary.empty
    assert "average_volatility_scale" in summary.columns
    assert "average_realised_annual_volatility" in summary.columns


def test_apply_volatility_target_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        apply_volatility_target(
            returns=bad_data,
            target_annual_volatility=0.15,
            lookback_days=20,
            max_leverage=1.0,
            output_ticker="bad",
        )
