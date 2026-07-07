import pandas as pd

from quantlab.backtesting.multi_ticker import run_multi_ticker_sma_backtest


def sample_prices(ticker: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": [ticker] * 10,
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "adj_close": [100, 101, 102, 103, 104, 103, 102, 101, 102, 103],
        }
    )


def test_run_multi_ticker_sma_backtest_returns_results_and_summary():
    prices_by_ticker = {
        "AAPL": sample_prices("AAPL"),
        "MSFT": sample_prices("MSFT"),
    }

    results, summary = run_multi_ticker_sma_backtest(
        prices_by_ticker=prices_by_ticker,
        short_window=2,
        long_window=3,
        transaction_cost_bps=5.0,
    )

    assert set(results["ticker"]) == {"AAPL", "MSFT"}
    assert set(summary["ticker"]) == {"AAPL", "MSFT"}
    assert "sharpe_ratio" in summary.columns
    assert "trade_count" in summary.columns
