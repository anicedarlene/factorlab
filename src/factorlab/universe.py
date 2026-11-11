import io
import pandas as pd

from pathlib import Path
from factorlab.config import RAW_DIR, DATA_DIR, UNIVERSE_PATH, TICKER_FIXES

def parse_ivv_holdings(path) -> pd.DataFrame:
    text = Path(path).read_text(encoding="utf-8-sig")
    lines = text.splitlines()

    header_idx = next(
        i for i, line in enumerate(lines) if "Ticker" in line and "Asset Class" in line
    )
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]

    ticker_col = next(c for c in df.columns if "Ticker" in c)

    #Keep only stocks, drop others
    df = df[df["Asset Class"].astype(str).str.strip() == "Equity"].copy()

    out = pd.DataFrame(
        {
            "ticker": df[ticker_col].astype(str).str.strip().str.upper(),
            "name": df["Name"],
            "sector": df["Sector"],
        }
    )
    out["ticker"] = (
    out["ticker"].replace(TICKER_FIXES).str.replace(r"[./\s]+", "-", regex=True)
    )
    bad = out[~out["ticker"].str.fullmatch(r"[A-Z0-9\-]+")]
    if len(bad):
        print("Dropped tickers with unexpected format:", bad["ticker"].tolist())
    out = out[out["ticker"].str.fullmatch(r"[A-Z0-9\-]+")]
    return out.drop_duplicates("ticker").sort_values("ticker").reset_index(drop=True)

def load_universe(refresh: bool = False) -> pd.DataFrame:
    """Load the saved universe, or build it from the newest IVV file in data/raw/."""
    if UNIVERSE_PATH.exists() and not refresh:
        return pd.read_csv(UNIVERSE_PATH)

    files = sorted(RAW_DIR.glob("IVV_holdings*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No IVV holdings file found in {RAW_DIR}. "
            "Download it from iShares and save it as IVV_holdings_YYYY-MM-DD.csv"
        )
    df = parse_ivv_holdings(files[-1])
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(UNIVERSE_PATH, index=False)
    return df

