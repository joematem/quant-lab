from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf
from loguru import logger

from quantlab.utils.paths import project_path


@dataclass(frozen=True)
class YahooPriceRequest:
    ticker: str
    start: str = "2015-01-01"
    end: str | None = None
    interval: str = "1d"


def normalize_yahoo_prices(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Clean Yahoo Finance OHLCV data into a stable research format."""
    if df.empty:
        raise ValueError(f"No price data returned for ticker: {ticker}")

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    column_map = {
        "Date": "date",
        "Datetime": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    }

    df = df.rename(columns=column_map)

    required_columns = ["date", "open", "high", "low", "close", "volume"]
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns for {ticker}: {missing}")

    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]

    df["ticker"] = ticker.upper()
    df["date"] = pd.to_datetime(df["date"]).dt.date

    ordered_columns = [
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]

    df = df[ordered_columns]
    df = df.dropna(subset=["open", "high", "low", "close", "adj_close"])
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    return df


def download_yahoo_prices(request: YahooPriceRequest) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance."""
    logger.info(
        "Downloading Yahoo Finance data",
        ticker=request.ticker,
        start=request.start,
        end=request.end,
        interval=request.interval,
    )

    raw = yf.download(
        tickers=request.ticker,
        start=request.start,
        end=request.end,
        interval=request.interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    return normalize_yahoo_prices(raw, request.ticker)


def save_prices_to_parquet(
    df: pd.DataFrame,
    ticker: str,
    output_dir: Path | None = None,
) -> Path:
    """Save price data to Parquet."""
    if output_dir is None:
        output_dir = project_path("data", "raw", "yahoo")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{ticker.upper()}.parquet"

    df.to_parquet(output_path, index=False)
    logger.info("Saved Yahoo price data", path=str(output_path), rows=len(df))

    return output_path
