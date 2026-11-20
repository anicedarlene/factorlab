import numpy as np
import pandas as pd

TRADING_DAYS = 252

def annual_return(r: pd.Series) -> float:
    return (1 + r).prod() ** (TRADING_DAYS / len(r)) - 1

def annual_vol(r: pd.Series) -> float:
    return r.std() * np.sqrt(TRADING_DAYS)

def sharpe(r: pd.Series) -> float:
    return r.mean() / r.std() * np.sqrt(TRADING_DAYS)

def max_drawdown(r: pd.Series) -> float:
    equity = (1 + r).cumprod()
    return (equity / equity.cummax() - 1).min()

def summary(res: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for col in ("gross", "net"):
        r = res[col]
        rows[col] = {
            "ann_return": annual_return(r),
            "ann_vol": annual_vol(r),
            "sharpe": sharpe(r),
            "max_drawdown": max_drawdown(r),
        }
    out = pd.DataFrame(rows)
    out.loc["avg_daily_turnover"] = res["turnover"].mean()
    return out.round(4)