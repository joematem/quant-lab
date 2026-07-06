import pandas as pd
import pytest

from quantlab.data.yahoo_prices import normalize_yahoo_prices


def test_normalize_yahoo_prices_returns_expected_columns():
    raw = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 100.0],
            "Close": [104.0, 105.0],
            "Adj Close": [104.0, 105.0],
            "Volume": [1_000_000, 1_100_000],
        }
    ).set_index("Date")

    result = normalize_yahoo_prices(raw, "AAPL")

    assert list(result.columns) == [
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]
    assert result["ticker"].unique().tolist() == ["AAPL"]
    assert len(result) == 2


def test_normalize_yahoo_prices_rejects_empty_data():
    with pytest.raises(ValueError, match="No price data returned"):
        normalize_yahoo_prices(pd.DataFrame(), "AAPL")
