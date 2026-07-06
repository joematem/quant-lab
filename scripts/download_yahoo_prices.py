from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from quantlab.data.yahoo_prices import (
    YahooPriceRequest,
    download_yahoo_prices,
    save_prices_to_parquet,
)

app = typer.Typer(help="Download Yahoo Finance price data.")
console = Console()

TickersArg = Annotated[
    list[str],
    typer.Argument(help="Ticker symbols, e.g. AAPL MSFT NVDA"),
]

StartOption = Annotated[
    str,
    typer.Option(help="Start date in YYYY-MM-DD format"),
]

EndOption = Annotated[
    str | None,
    typer.Option(help="End date in YYYY-MM-DD format"),
]

IntervalOption = Annotated[
    str,
    typer.Option(help="Data interval"),
]


@app.command()
def main(
    tickers: TickersArg,
    start: StartOption = "2015-01-01",
    end: EndOption = None,
    interval: IntervalOption = "1d",
) -> None:
    for ticker in tickers:
        request = YahooPriceRequest(
            ticker=ticker,
            start=start,
            end=end,
            interval=interval,
        )
        df = download_yahoo_prices(request)
        output_path = save_prices_to_parquet(df, ticker)

        console.print(
            f"[green]Saved {ticker.upper()}[/green]: "
            f"{len(df):,} rows -> {output_path}"
        )


if __name__ == "__main__":
    app()
