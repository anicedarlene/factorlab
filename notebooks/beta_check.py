import pandas as pd

from factorlab.data import load_prices
from factorlab.engine import run_backtest
from factorlab.signals import compute_returns, low_volatility, momentum_12_1, reversal_1m

prices = load_prices()
returns = compute_returns(prices)
market = returns.mean(axis=1)  #equal-weighted average return of all stocks

signals = {
    "momentum_12_1": momentum_12_1(prices),
    "low_volatility": low_volatility(returns),
    "reversal_1m": reversal_1m(prices),
}

for name, sig in signals.items():
    strat = run_backtest(sig, returns, rebalance_every=21)["gross"]
    df = pd.concat([strat, market], axis=1, keys=["strat", "mkt"]).loc["2016-01-04":].dropna()
    beta = df.cov().loc["strat", "mkt"] / df["mkt"].var()
    resid = df["strat"] - beta * df["mkt"]
    print(f"  beta-hedged Sharpe: {resid.mean() / resid.std() * 252 ** 0.5:.2f}")
    print(f"  raw gross Sharpe:   {df['strat'].mean() / df['strat'].std() * 252 ** 0.5:.2f}")
    print(f"{name}: market beta = {beta:.3f}")