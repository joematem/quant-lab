import pandas as pd

from quantlab.data.duckdb_prices import (
    connect_duckdb,
    query_prices,
    summarize_prices,
)


def test_duckdb_price_summary_from_mock_view():
    connection = connect_duckdb()

    mock_prices = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-01"],
            "open": [100.0, 101.0, 200.0],
            "high": [105.0, 106.0, 205.0],
            "low": [99.0, 100.0, 198.0],
            "close": [104.0, 105.0, 204.0],
            "adj_close": [104.0, 105.0, 204.0],
            "volume": [1_000_000, 1_100_000, 2_000_000],
        }
    )

    connection.register("mock_prices", mock_prices)
    connection.execute("""
        CREATE OR REPLACE VIEW yahoo_prices AS
        SELECT
            ticker,
            CAST(date AS DATE) AS date,
            open,
            high,
            low,
            close,
            adj_close,
            volume
        FROM mock_prices
        """)

    summary = summarize_prices(connection)

    assert set(summary["ticker"]) == {"AAPL", "MSFT"}
    assert summary.loc[summary["ticker"] == "AAPL", "rows"].iloc[0] == 2


def test_query_prices_filters_ticker():
    connection = connect_duckdb()

    mock_prices = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            "date": ["2024-01-01", "2024-01-01"],
            "open": [100.0, 200.0],
            "high": [105.0, 205.0],
            "low": [99.0, 198.0],
            "close": [104.0, 204.0],
            "adj_close": [104.0, 204.0],
            "volume": [1_000_000, 2_000_000],
        }
    )

    connection.register("mock_prices", mock_prices)
    connection.execute("""
        CREATE OR REPLACE VIEW yahoo_prices AS
        SELECT
            ticker,
            CAST(date AS DATE) AS date,
            open,
            high,
            low,
            close,
            adj_close,
            volume
        FROM mock_prices
        """)

    result = query_prices(connection, ticker="AAPL")

    assert len(result) == 1
    assert result["ticker"].iloc[0] == "AAPL"
