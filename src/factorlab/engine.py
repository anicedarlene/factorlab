import numpy as np
import pandas as pd

def quintile_weights(signal: pd.DataFrame, q: float = 0.2) -> pd.DataFrame:
    """Each day: long the top q of stocks, short the bottom q, equal-weighted.
    Long side sums to +0.5 and short side to -0.5 (total exposure 1)."""
    ranks = signal.rank(axis=1, pct=True)
    valid = signal.notna()
    longs = ((ranks > 1 - q) & valid).astype(float)
    shorts = ((ranks <= q) & valid).astype(float)
    n_long = longs.sum(axis=1).replace(0, np.nan)
    n_short = shorts.sum(axis=1).replace(0, np.nan)
    weights = longs.div(n_long, axis=0) * 0.5 - shorts.div(n_short, axis=0) * 0.5
    return weights.fillna(0.0)

def run_backtest(
    signal: pd.DataFrame,
    returns: pd.DataFrame,
    cost_bps: float = 10.0,
    q: float = 0.2,
    rebalance_every: int = 1,
) -> pd.DataFrame:
    weights = quintile_weights(signal, q)
    if rebalance_every > 1:
        rebal = weights.iloc[::rebalance_every]
        weights = rebal.reindex(weights.index).ffill().fillna(0.0)
    held = weights.shift(1)  
    gross = (held * returns).sum(axis=1)
    turnover = held.diff().abs().sum(axis=1)  
    cost = turnover * cost_bps / 10_000
    return pd.DataFrame(
        {"gross": gross, "turnover": turnover, "cost": cost, "net": gross - cost}
    )
