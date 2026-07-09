import pandas as pd
import pytest

from quantlab.backtesting.portfolio import (
    build_equal_weight_portfolio_returns,
    summarize_equal_weight_portfolio,
)


def sample_backtest_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT", "AAPL", "MSFT"],
            "date": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-02",
                "2024-01-02",
            ],
            "strategy_net_return": [0.01, 0.03, -0.02, 0.01],
            "daily_return": [0.02, 0.04, -0.01, 0.03],
        }
    )


def test_build_equal_weight_portfolio_returns():
    portfolio = build_equal_weight_portfolio_returns(
        backtest_results=sample_backtest_results(),
        return_column="strategy_net_return",
        portfolio_name="equal_weight_sma",
    )

    assert len(portfolio) == 2
    assert set(portfolio["ticker"]) == {"equal_weight_sma"}
    assert "daily_return" in portfolio.columns
    assert "adj_close" in portfolio.columns
    assert portfolio.loc[0, "daily_return"] == pytest.approx(0.02)


def test_summarize_equal_weight_portfolio():
    portfolio = build_equal_weight_portfolio_returns(
        backtest_results=sample_backtest_results(),
        return_column="strategy_net_return",
        portfolio_name="equal_weight_sma",
    )

    summary = summarize_equal_weight_portfolio(portfolio)

    assert not summary.empty
    assert "total_return" in summary.columns
    assert "average_asset_count" in summary.columns


def test_build_equal_weight_portfolio_rejects_missing_columns():
    bad_data = pd.DataFrame({"ticker": ["AAPL"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        build_equal_weight_portfolio_returns(
            backtest_results=bad_data,
            return_column="strategy_net_return",
            portfolio_name="bad",
        )
