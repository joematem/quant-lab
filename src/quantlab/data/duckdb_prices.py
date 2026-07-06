from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from quantlab.utils.paths import project_path

DEFAULT_YAHOO_PARQUET_GLOB = "data/raw/yahoo/*.parquet"


def connect_duckdb(database_path: Path | str = ":memory:") -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection."""
    return duckdb.connect(str(database_path))


def _sql_string_literal(value: str) -> str:
    """Return a safe SQL string literal."""
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def load_yahoo_prices(
    connection: duckdb.DuckDBPyConnection,
    parquet_glob: str = DEFAULT_YAHOO_PARQUET_GLOB,
) -> None:
    """Create or replace a DuckDB view over Yahoo Parquet files."""
    full_glob = str(project_path(parquet_glob))
    parquet_glob_sql = _sql_string_literal(full_glob)

    connection.execute(f"""
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
        FROM read_parquet({parquet_glob_sql})
        """)


def query_prices(
    connection: duckdb.DuckDBPyConnection,
    ticker: str,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Query prices for one ticker."""
    sql = """
        SELECT *
        FROM yahoo_prices
        WHERE ticker = ?
    """
    params: list[str] = [ticker.upper()]

    if start is not None:
        sql += " AND date >= ?"
        params.append(start)

    if end is not None:
        sql += " AND date <= ?"
        params.append(end)

    sql += " ORDER BY date"

    return connection.execute(sql, params).df()


def calculate_daily_returns(
    connection: duckdb.DuckDBPyConnection,
) -> pd.DataFrame:
    """Calculate simple daily returns from adjusted close prices."""
    return connection.execute("""
        SELECT
            ticker,
            date,
            adj_close,
            adj_close / LAG(adj_close) OVER (
                PARTITION BY ticker
                ORDER BY date
            ) - 1 AS daily_return
        FROM yahoo_prices
        ORDER BY ticker, date
        """).df()


def summarize_prices(
    connection: duckdb.DuckDBPyConnection,
) -> pd.DataFrame:
    """Create a ticker-level summary table."""
    return connection.execute("""
        SELECT
            ticker,
            MIN(date) AS start_date,
            MAX(date) AS end_date,
            COUNT(*) AS rows,
            MIN(adj_close) AS min_adj_close,
            MAX(adj_close) AS max_adj_close,
            AVG(volume) AS avg_volume
        FROM yahoo_prices
        GROUP BY ticker
        ORDER BY ticker
        """).df()
