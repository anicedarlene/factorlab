from factorlab.data import load_prices
from factorlab.engine import run_backtest
from factorlab.metrics import summary
from factorlab.signals import compute_returns, momentum_12_1

prices = load_prices()
returns = compute_returns(prices)
signal = momentum_12_1(prices)

for n in (1, 5, 21):
    res = run_backtest(signal, returns, rebalance_every=n).loc["2016-01-04":]
    print(f"\n=== momentum, rebalance every {n} day(s) ===")
    print(summary(res))