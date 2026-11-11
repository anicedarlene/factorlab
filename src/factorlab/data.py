import time
from pathlib import Path

import duckdb
import pandas as pd
import yfinance as yf

from factorlab.config import BATCH_SIZE, DB_PATH, MAX_RETRIES, PAUSE_SECONDS, START_DATE

def get_connection(path=DB_PATH) -> duckdb.DuckDBPyConnection:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            date DATE NOT NULL,
            ticker VARCHAR NOT NULL,
            adj_close DOUBLE NOT NULL,
            volume BIGINT,
            PRIMARY KEY (date, ticker)
        )
        """
    )
    return con

def to_long(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    close = raw["Close"]
    volume = raw["Volume"]
    if isinstance(close, pd.Series):  #a single ticker can come back as a Series
        close = close.to_frame(tickers[0])
        volume = volume.to_frame(tickers[0])

    close = (
        close.rename_axis("date")
        .reset_index()
        .melt(id_vars="date", var_name="ticker", value_name="adj_close")
    )
    volume = (
        volume.rename_axis("date")
        .reset_index()
        .melt(id_vars="date", var_name="ticker", value_name="volume")
    )

    df = close.merge(volume, on=["date", "ticker"], how="left")
    df = df.dropna(subset=["adj_close"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["volume"] = df["volume"].fillna(0).astype("int64")
    return df[["date", "ticker", "adj_close", "volume"]]

def download_batch(tickers: list[str], start: str = START_DATE) -> pd.DataFrame:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = yf.download(
                tickers, start=start, auto_adjust=True, progress=False, threads=True
            )
            if raw is not None and not raw.empty:
                return to_long(raw, tickers)
            print(f"  empty result (attempt {attempt}/{MAX_RETRIES})")
        except Exception as e:
            print(f"  error: {e} (attempt {attempt}/{MAX_RETRIES})")
        time.sleep(PAUSE_SECONDS * attempt * 2)  #wait longer after each failure
    return pd.DataFrame(columns=["date", "ticker", "adj_close", "volume"])

def store(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    con.register("batch_df", df)
    con.execute(
        "INSERT OR REPLACE INTO prices "
        "SELECT date, ticker, adj_close, volume FROM batch_df"
    )
    con.unregister("batch_df")
    return len(df)


def update_prices(tickers: list[str], con=None) -> list[str]:
    con = con or get_connection()
    done = set(con.execute("SELECT DISTINCT ticker FROM prices").fetchdf()["ticker"])
    todo = [t for t in tickers if t not in done]
    print(f"{len(done)} tickers already stored, {len(todo)} to download")

    failed = []
    for i in range(0, len(todo), BATCH_SIZE):
        batch = todo[i : i + BATCH_SIZE]
        print(f"Batch {i // BATCH_SIZE + 1}: {len(batch)} tickers")
        df = download_batch(batch)
        got = set(df["ticker"].unique())
        failed += [t for t in batch if t not in got]
        store(con, df)
        time.sleep(PAUSE_SECONDS)

    print(f"Done. Failed tickers ({len(failed)}): {failed}")
    return failed