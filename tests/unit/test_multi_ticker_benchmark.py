import pandas as pd

from quantlab.backtesting.multi_ticker_benchmark import (
    compare_multi_ticker_sma_to_buy_and_hold,
)


def sample_prices(ticker: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": [ticker] * 10,
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "adj_close": [100, 101, 102, 103, 104, 103, 102, 101, 102, 103],
        }
    )


def test_compare_multi_ticker_sma_to_buy_and_hold():
    prices_by_ticker = {
        "AAPL": sample_prices("AAPL"),
        "MSFT": sample_prices("MSFT"),
    }

    comparison, summary = compare_multi_ticker_sma_to_buy_and_hold(
        prices_by_ticker=prices_by_ticker,
        short_window=2,
        long_window=3,
        transaction_cost_bps=5.0,
    )

    assert set(comparison["ticker"]) == {"AAPL", "MSFT"}
    assert set(comparison["strategy"]) == {"sma_crossover", "buy_and_hold"}
    assert set(summary["ticker"]) == {"AAPL", "MSFT"}
    assert set(summary["strategy"]) == {"sma_crossover", "buy_and_hold"}
