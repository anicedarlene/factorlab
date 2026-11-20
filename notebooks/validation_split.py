from factorlab.data import load_prices
from factorlab.engine import run_backtest
from factorlab.metrics import summary
from factorlab.signals import compute_returns, low_volatility, momentum_12_1, reversal_1m

prices = load_prices()
returns = compute_returns(prices)
signals = {
    "momentum_12_1": momentum_12_1(prices),
    "low_volatility": low_volatility(returns),
    "reversal_1m": reversal_1m(prices),
}
periods = {"in-sample 2016-2023": ("2016-01-04", "2023-12-29"),
           "hold-out 2024-2026": ("2024-01-02", "2026-11-10")}

for name, sig in signals.items():
    res = run_backtest(sig, returns, rebalance_every=21)
    for label, (a, b) in periods.items():
        r = res.loc[a:b]
        equity = (1 + r["net"]).cumprod()
        trough = (equity / equity.cummax() - 1).idxmin().date()
        print(f"\n=== {name} | {label} | worst drawdown trough: {trough} ===")
        print(summary(r))