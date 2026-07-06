import pandas as pd

from quantlab.research_performance import (
    calculate_cumulative_returns,
    calculate_drawdowns,
    summarize_performance,
)


def test_calculate_cumulative_returns():
    returns = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "adj_close": [100.0, 110.0, 121.0],
            "daily_return": [None, 0.10, 0.10],
        }
    )

    result = calculate_cumulative_returns(returns)

    assert round(result["cumulative_return"].iloc[-1], 4) == 0.21


def test_calculate_drawdowns():
    returns = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL", "AAPL"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "adj_close": [100.0, 110.0, 99.0, 120.0],
            "daily_return": [None, 0.10, -0.10, 0.212121],
        }
    )

    result = calculate_drawdowns(returns)

    assert result["drawdown"].min() < 0


def test_summarize_performance_returns_expected_columns():
    returns = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "adj_close": [100.0, 101.0, 102.0],
            "daily_return": [None, 0.01, 0.009901],
        }
    )

    result = summarize_performance(returns)

    assert list(result.columns) == [
        "ticker",
        "observations",
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "best_daily_return",
        "worst_daily_return",
    ]
    assert result["ticker"].iloc[0] == "AAPL"
