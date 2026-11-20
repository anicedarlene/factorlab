import numpy as np
import pandas as pd

def forward_returns(prices: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Return earned over the next `horizon` days. Uses future data ON PURPOSE:
    this is the outcome we judge the signal against, never an input to it."""
    return prices.shift(-horizon) / prices - 1

def daily_ic(signal: pd.DataFrame, fwd: pd.DataFrame, min_stocks: int = 50) -> pd.Series:
    """Spearman rank correlation across stocks, one value per day."""
    valid = signal.notna() & fwd.notna()
    s = signal.where(valid).rank(axis=1)
    r = fwd.where(valid).rank(axis=1)
    ic = s.corrwith(r, axis=1)  #Pearson on ranks = Spearman
    ic[valid.sum(axis=1) < min_stocks] = np.nan
    return ic.dropna()

def ic_summary(ic: pd.Series) -> pd.Series:
    return pd.Series(
        {
            "mean_ic": ic.mean(),
            "std_ic": ic.std(),
            "icir": ic.mean() / ic.std(),
            "t_stat": ic.mean() / ic.std() * np.sqrt(len(ic)),
            "pct_positive": (ic > 0).mean(),
            "n_days": len(ic),
        }
    ).round(4)

def quintile_returns(signal: pd.DataFrame, returns: pd.DataFrame, n: int = 5) -> pd.Series:
    """Annualized average next-day return of each quintile (Q1 = weakest signal)."""
    bucket = np.ceil(signal.rank(axis=1, pct=True) * n).clip(1, n)
    fwd = returns.shift(-1)  #signal at close t -> return of day t+1, same timing as the engine
    out = {f"Q{k}": fwd.where(bucket == k).mean(axis=1).mean() * 252 for k in range(1, n + 1)}
    return pd.Series(out).round(4)