import pandas as pd
import pytest

from quantlab.backtesting.portfolio_analysis import (
    create_portfolio_strategy_ranking,
)


def sample_portfolio_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": [
                "equal_weight_buy_hold",
                "equal_weight_sma",
                "equal_weight_sma_vol_targeted",
            ],
            "total_return": [4.0, 1.0, 0.8],
            "annualized_return": [0.30, 0.18, 0.15],
            "annualized_volatility": [0.25, 0.20, 0.15],
            "sharpe_ratio": [1.2, 0.9, 1.0],
            "max_drawdown": [-0.40, -0.30, -0.20],
            "average_asset_count": [3.0, 3.0, None],
            "average_volatility_scale": [None, None, 0.8],
        }
    )


def test_create_portfolio_strategy_ranking_orders_by_sharpe():
    ranking = create_portfolio_strategy_ranking(sample_portfolio_summary())

    assert list(ranking["rank"]) == [1, 2, 3]
    assert ranking.iloc[0]["ticker"] == "equal_weight_buy_hold"
    assert "return_to_drawdown" in ranking.columns


def test_create_portfolio_strategy_ranking_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["equal_weight_sma"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        create_portfolio_strategy_ranking(bad_data)
